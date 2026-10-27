<h1 align="center">
    <picture>
        <source media="(prefers-color-scheme: dark)" srcset="assets/emg_bids_banner_dark.svg">
        <source media="(prefers-color-scheme: light)" srcset="assets/emg_bids_banner_light.svg">
        <img alt="EMG-BIDS Converter" src="assets/emg_bids_banner_light.svg" width="600">
    </picture>
</h1>

EMG-BIDS Converter is an open-source Python package for converting electromyography (EMG) recordings from proprietary
formats to the Brain Imaging Data Structure (BIDS) standard, following the EMG-BIDS extension
(Shirazi et al., 2026).

## Supported formats

| Format | Manufacturer | Extension |
|--------|--------------|-----------|
| OTB4   | OT Bioelettronica | `.otb4` |

## Installation

Requires Python 3.12 or later and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/ToNIC-Inserm/emg-bids-converter.git
cd emg-bids-converter
uv sync
```

## Quick Start

Create an empty dataset, then add recordings one by one:

```bash
uv run emg-bids init my_dataset --name "My study" --author "J. Doe" --license CC-BY-4.0

uv run emg-bids add my_dataset recordings/S01_mvc1.otb4 --subject 01 --task mvc --run 1 --emg-reference "patella"
uv run emg-bids add my_dataset recordings/S01_mvc2.otb4 --subject 01 --task mvc --run 2 --emg-reference "patella"
```

This produces:

```
my_dataset/
├── README.md
├── dataset_description.json
├── participants.json
├── participants.tsv
└── sub-01/
    └── emg/
        ├── sub-01_task-mvc_run-1_channels.tsv
        ├── sub-01_task-mvc_run-1_emg.bdf
        ├── sub-01_task-mvc_run-1_emg.json
        └── ...
```

Optional entities: `--session`, `--acquisition`, `--recording`. The power line frequency defaults to 50 Hz
(`--powerline-frequency 60` otherwise). Run `uv run emg-bids add --help` for all options.

Check the result with the [BIDS validator](https://github.com/bids-standard/bids-validator):

```bash
bids-validator my_dataset
```

## Graphical interface

```bash
uv run emg-bids-gui
```

⚠️ The graphical interface is under development ⚠️

## Python API

```python
from pathlib import Path

from emg_bids_converter.api import convert_recording, create_dataset
from emg_bids_converter.models.emg.entities import Entities

root = Path("my_dataset")
create_dataset(root, "My study", authors=["J. Doe"], license="CC-BY-4.0")
convert_recording(root, Path("recordings/S01_mvc1.otb4"), Entities(subject="01", task="mvc", run="1"),
                  emg_reference="patella")
```

To convert a whole folder, `emg_bids_converter.batch` finds the recordings with path patterns such as
`{subject}/**/{task}_{run}.otb4`, and `api.add_recordings` converts the resulting plan after checking it.

## Development

```bash
uv run pytest
```

## References

Shirazi, S. Y., McCloy, D., Oostenveld, R., Boonstra, T., Larson, E., Welzel, J., Gau, R., Markiewicz, C. J.,
Posella, S., Horschig, J. M., Klotz, T., Gramfort, A., & Delorme, A. (2026). EMG-BIDS: an extension to the Brain
Imaging Data Structure for electromyography. *bioRxiv*, 2026.07.21.739911.
https://doi.org/10.64898/2026.07.21.739911

## Author and citation

EMG-BIDS Converter is developed by Hugo Haffad at the ToNIC laboratory (Univ Toulouse, Inserm, UMR 1214, Toulouse, France) under the supervision of Prof. David Amarantini and Prof. David Gasq.

If you use this software in your research, please cite it: use the *Cite this repository* button on GitHub, or see [CITATION.cff](CITATION.cff).

## License

[MIT](LICENSE)
