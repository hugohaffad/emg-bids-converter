"""End-to-end: OTB4 file -> Recording -> write_dataset -> BDF read back -> bids-validator.

Runs on every data/*.otb4 file of the repository, or on the single file given by EMG_BIDS_OTB4.
The bids-validator step needs the `bids-validator` executable on the PATH
(deno install -ERWN -g -n bids-validator jsr:@bids/validator); otherwise the test is skipped.
"""

import os
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
from pyedflib import highlevel

from emg_bids_converter.models.dataset import Dataset
from emg_bids_converter.models.dataset_description import DatasetDescription
from emg_bids_converter.models.emg.entities import Entities
from emg_bids_converter.models.participants import Participant
from emg_bids_converter.readers import otb4
from emg_bids_converter.writers.dataset import write_dataset

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _otb4_samples() -> list[Path]:
    if os.environ.get("EMG_BIDS_OTB4"):
        return [Path(os.environ["EMG_BIDS_OTB4"])]
    return sorted((_REPO_ROOT / "data").glob("*.otb4"))


def _bids_validator(root: Path) -> None:
    """Run bids-validator on root and fail the test on any error; skip if it is not installed"""
    executable = shutil.which("bids-validator")
    if executable is None:
        pytest.skip("bids-validator is not installed")
    result = subprocess.run([executable, str(root)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("path", _otb4_samples(), ids=lambda p: p.name)
def test_otb4_dataset_is_valid_bids(tmp_path, path):
    recording = otb4.read(path, task_name="mvc", emg_reference="Not specified (end-to-end test)")
    dataset = Dataset(
        description=DatasetDescription(Name="OTB4 end-to-end test", BIDSVersion="1.11.1"),
        participants=[Participant(participant_id="sub-01")],
        recordings=[(Entities(subject="01", task="mvc"), recording)],
    )
    root = tmp_path / "ds"
    write_dataset(root, dataset)

    # The BDF read back gives the reader's signal, up to 24-bit quantization
    signals, headers, _ = highlevel.read_edf(str(root / "sub-01/emg/sub-01_task-mvc_emg.bdf"))
    assert [h["label"] for h in headers] == [c.name__channels for c in recording.channels]
    n_samples = recording.signal.shape[1]
    bound = float(np.ceil(np.abs(recording.signal).max()))
    np.testing.assert_allclose(np.asarray(signals)[:, :n_samples], recording.signal, rtol=0, atol=bound / 2**22)

    _bids_validator(root)



def test_cli_init_then_add_every_otb4_sample(tmp_path):
    """emg-bids init, then emg-bids add for each OTB4 sample (one subject each), gives a valid BIDS dataset"""
    from emg_bids_converter.cli import main

    samples = _otb4_samples()
    if not samples:
        pytest.skip("no OTB4 sample (set EMG_BIDS_OTB4 or put a file in data/)")
    root = tmp_path / "ds"

    assert main(["init", str(root), "--name", "CLI end-to-end test", "--author", "Test Author"]) == 0
    for i, path in enumerate(samples, start=1):
        assert main([
            "add", str(root), str(path),
            "--subject", f"{i:02d}", "--task", "mvc", "--emg-reference", "Not specified (end-to-end test)",
        ]) == 0

    subjects = [f"sub-{i:02d}" for i in range(1, len(samples) + 1)]
    assert (root / "participants.tsv").read_text(encoding="utf-8").splitlines() == ["participant_id", *subjects]
    # adding the same recording twice is refused, and leaves the dataset as it was
    assert main(["add", str(root), str(samples[0]), "--subject", "01", "--task", "mvc", "--emg-reference", "x"]) == 1
    _bids_validator(root)


def test_scan_rename_map_then_add_recordings(tmp_path):
    """A folder in an arbitrary layout -> scan with a pattern -> renamed labels -> mapping round trip -> valid BIDS"""
    from emg_bids_converter.api import add_recordings, create_dataset
    from emg_bids_converter.batch.mapping import read_mapping, write_mapping
    from emg_bids_converter.batch.plan import build_plan
    from emg_bids_converter.batch.scan import scan

    samples = _otb4_samples()
    if not samples:
        pytest.skip("no OTB4 sample (set EMG_BIDS_OTB4 or put a file in data/)")
    source = tmp_path / "source"
    for i, sample in enumerate(samples, start=1):
        folder = source / f"Patient {i}" / "day 1"
        folder.mkdir(parents=True)
        (folder / f"MVC max-{i}.otb4").symlink_to(sample.resolve())
    (source / "notes.otb4").write_bytes(b"")  # matches no pattern

    files, unmatched = scan(source, ["{subject}/**/{task}-{run}.otb4"])
    assert unmatched == [source / "notes.otb4"]
    assert [file.values for file in files] == [
        {"subject": f"Patient {i}", "task": "MVC max", "run": str(i)} for i in range(1, len(samples) + 1)
    ]

    labels = {"subject": {f"Patient {i}": f"{i:02d}" for i in range(1, len(samples) + 1)},
              "task": {"MVC max": "mvc"}}
    plan = build_plan(files, labels)
    write_mapping(plan, tmp_path / "mapping.tsv")
    assert build_plan(read_mapping(tmp_path / "mapping.tsv")) == plan

    root = tmp_path / "ds"
    create_dataset(root, "Batch end-to-end test")
    calls = []
    add_recordings(root, plan, "Not specified (end-to-end test)", progress=lambda i, n, item: calls.append(i))
    assert calls == list(range(len(samples)))
    assert (root / "sub-01/emg/sub-01_task-mvc_run-1_emg.bdf").is_file()
    # a second conversion of the same plan is refused before anything is written
    with pytest.raises(FileExistsError):
        add_recordings(root, plan, "x")
    _bids_validator(root)
