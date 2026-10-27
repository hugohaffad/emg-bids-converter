from collections.abc import Callable, Sequence
from importlib.metadata import version
from pathlib import Path

from .batch.plan import PlannedRecording, check_plan
from .core.schema import load
from .models.dataset_description import DatasetDescription
from .models.emg.entities import Entities
from .readers import read
from .writers.dataset import add_recording, init_dataset
from .writers.emg.naming import build_directory, build_filename

PACKAGE = "emg-bids-converter"
CODE_URL = "https://github.com/ToNIC-Inserm/emg_bids_converter"


def create_dataset(root: Path, name: str, authors: list[str] | None = None,
                   license: str | None = None) -> list[Path]:
    """Create an empty BIDS dataset under root; return the written paths"""
    description = DatasetDescription(
        Name=name,
        BIDSVersion=load()["bids_version"],
        Authors=authors,
        License=license,
        GeneratedBy=[{"Name": PACKAGE, "Version": version(PACKAGE), "CodeURL": CODE_URL}],
    )
    return init_dataset(root, description)


def convert_recording(root: Path, file: Path, entities: Entities, emg_reference: str,
                      powerline_frequency: float = 50.0) -> list[Path]:
    """Read one recording file and add it to the dataset under root; return the written paths"""
    recording = read(
        file,
        task_name=entities.task,
        emg_reference=emg_reference,
        powerline_frequency=powerline_frequency,
    )
    return add_recording(root, entities, recording)


def add_recordings(root: Path, plan: Sequence[PlannedRecording], emg_reference: str,
                   powerline_frequency: float = 50.0,
                   progress: Callable[[int, int, PlannedRecording], None] | None = None) -> list[Path]:
    """Convert every recording of the plan into the dataset under root; return the written paths.

    The whole plan is checked first (files, duplicates, recordings already in the dataset), so that
    a predictable problem stops the conversion before anything is written. progress, if given, is
    called before each recording with (index, total, recording).
    """
    root = Path(root)
    check_plan(plan)
    for item in plan:
        target = build_directory(root, item.entities) / build_filename(item.entities, "emg", ".bdf")
        if target.exists():
            raise FileExistsError(f"{target} already exists ({item.source.name})")

    written = []
    for index, item in enumerate(plan):
        if progress is not None:
            progress(index, len(plan), item)
        written += convert_recording(root, item.source, item.entities, emg_reference, powerline_frequency)
    return written
