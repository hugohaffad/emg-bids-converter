"""Read and write a conversion plan as a table: one row per recording, one column per entity.

Tab-separated for .tsv files, comma-separated otherwise. The source column holds the file path,
relative to the table's folder or absolute; empty cells and "n/a" mean "no value".
"""

import csv
from collections.abc import Sequence
from pathlib import Path

from .patterns import ENTITIES
from .plan import PlannedRecording, SourceFile

COLUMNS = ("source", *ENTITIES)


def _delimiter(path: Path) -> str:
    return "\t" if path.suffix.lower() == ".tsv" else ","


def write_mapping(plan: Sequence[PlannedRecording], path: Path) -> None:
    """Write the plan with absolute source paths"""
    path = Path(path)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, delimiter=_delimiter(path), lineterminator="\n")
        writer.writerow(COLUMNS)
        for item in plan:
            values = [getattr(item.entities, entity) or "" for entity in ENTITIES]
            writer.writerow([str(item.source.absolute()), *values])


def read_mapping(path: Path) -> list[SourceFile]:
    """Read a table into source files with raw values; build_plan checks them"""
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=_delimiter(path))
        header = reader.fieldnames or []
        unknown = [column for column in header if column not in COLUMNS]
        if "source" not in header or unknown:
            raise ValueError(f"{path.name}: columns must be among {', '.join(COLUMNS)} with at least source"
                             + (f" (unknown: {', '.join(unknown)})" if unknown else ""))
        files = []
        for line, row in enumerate(reader, start=2):
            source = (row.get("source") or "").strip()
            if not source:
                raise ValueError(f"{path.name}, line {line}: empty source")
            values = {entity: value.strip() for entity in ENTITIES
                      if (value := row.get(entity) or "").strip() and value.strip() != "n/a"}
            files.append(SourceFile(path.parent / source, values))
    return files
