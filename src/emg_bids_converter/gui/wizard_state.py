"""What the New dataset wizard has collected so far, shared by its pages"""

from dataclasses import dataclass, field
from pathlib import Path

from ..batch.plan import PlannedRecording, SourceFile


@dataclass
class WizardState:
    files: list[SourceFile] = field(default_factory=list)                    # found by scans or imported
    unmatched: list[Path] = field(default_factory=list)                      # scanned files no pattern matched
    labels: dict[str, dict[str, str]] = field(default_factory=dict)          # entity -> raw value -> BIDS label
    overrides: dict[Path, dict[str, str | None]] = field(default_factory=dict)  # source -> entity -> label
    plan: list[PlannedRecording] = field(default_factory=list)               # set when the review page is valid
