"""Find the recording files of a folder and the raw entity values their paths contain"""

from collections.abc import Sequence
from pathlib import Path

from ..readers import READERS
from .labels import natural_key
from .patterns import compile_pattern, match
from .plan import SourceFile


def scan(folder: Path, patterns: Sequence[str]) -> tuple[list[SourceFile], list[Path]]:
    """Apply the first matching pattern to every supported file under folder; return (matched, unmatched)"""
    folder = Path(folder)
    if not folder.is_dir():
        raise NotADirectoryError(f"{folder} is not a folder")
    for pattern in patterns:
        compile_pattern(pattern)  # report a bad pattern even if no file reaches it

    paths = sorted((path for path in folder.rglob("*") if path.is_file() and path.suffix.lower() in READERS),
                   key=lambda path: natural_key(path.relative_to(folder).as_posix()))
    matched, unmatched = [], []
    for path in paths:
        relative = path.relative_to(folder).as_posix()
        values = next((values for pattern in patterns if (values := match(pattern, relative)) is not None), None)
        if values is None:
            unmatched.append(path)
        else:
            matched.append(SourceFile(path, {entity: value for entity, value in values.items() if value}))
    return matched, unmatched
