"""The conversion plan: which source file becomes which BIDS recording"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from ..models.emg.entities import Entities
from ..readers import READERS


@dataclass(frozen=True)
class SourceFile:
    """A recording file and the raw entity values found for it (not yet BIDS labels)"""
    source: Path
    values: Mapping[str, str]


@dataclass(frozen=True)
class PlannedRecording:
    """A recording file and the BIDS entities it will be converted to"""
    source: Path
    entities: Entities


def build_plan(files: Sequence[SourceFile],
               labels: Mapping[str, Mapping[str, str]] | None = None) -> list[PlannedRecording]:
    """Turn raw values into entities, renaming them with labels[entity][raw value] when given"""
    labels = labels or {}
    plan = []
    for file in files:
        values = {entity: labels.get(entity, {}).get(value, value)
                  for entity, value in file.values.items() if value}
        missing = [entity for entity in ("subject", "task") if entity not in values]
        if missing:
            raise ValueError(f"{file.source.name}: no {' and no '.join(missing)}")
        try:
            entities = Entities(**values)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{file.source.name}: {error}") from error
        plan.append(PlannedRecording(file.source, entities))
    return plan


def check_plan(plan: Sequence[PlannedRecording]) -> None:
    """Raise if the plan cannot be converted as a whole, before anything is written"""
    if not plan:
        raise ValueError("the plan has no recording")
    seen: dict[Entities, Path] = {}
    for item in plan:
        if not item.source.is_file():
            raise FileNotFoundError(f"{item.source} does not exist")
        if item.source.suffix.lower() not in READERS:
            raise ValueError(f"unsupported file type {item.source.suffix!r} ({item.source.name})")
        if item.entities in seen:
            raise ValueError(f"{seen[item.entities].name} and {item.source.name} have the same entities; "
                             f"they would be converted to the same BIDS file")
        seen[item.entities] = item.source
