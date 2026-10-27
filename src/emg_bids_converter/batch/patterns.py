"""Extract raw BIDS entity values from a file path with a user-written pattern.

A pattern describes a path relative to the scanned folder, with "/" between folders:
- {subject}, {session}, {task}, {acquisition}, {run} and {recording} capture a value;
  {run} captures digits only, the others any text within one path part, as short as possible;
  a placeholder used twice must capture the same text both times;
- * matches any text within one path part, ** any number of folders (none included);
- everything else is literal; letter case is ignored.

Example: "{subject}/**/{task}_{run}.otb4" matches "Patient 1/day 1/mvc_2.otb4"
with subject="Patient 1", task="mvc", run="2".
"""

import re
from functools import cache

ENTITIES = ("subject", "session", "task", "acquisition", "run", "recording")

_TOKEN = re.compile(r"\{(\w+)\}|\*\*/|\*\*|\*")


@cache
def compile_pattern(pattern: str) -> re.Pattern[str]:
    """Translate a pattern into a regular expression; raise ValueError on an unknown placeholder"""
    parts = []
    seen = set()
    position = 0
    for token in _TOKEN.finditer(pattern):
        parts.append(re.escape(pattern[position:token.start()]))
        position = token.end()
        name = token.group(1)
        if name is not None:
            if name not in ENTITIES:
                raise ValueError(f"unknown placeholder {{{name}}} in {pattern!r}; "
                                 f"use {', '.join('{' + entity + '}' for entity in ENTITIES)}")
            if name in seen:
                parts.append(f"(?P={name})")
            else:
                seen.add(name)
                parts.append(f"(?P<{name}>[0-9]+)" if name == "run" else f"(?P<{name}>[^/]+?)")
        elif token.group(0) == "**/":
            parts.append("(?:[^/]+/)*")
        elif token.group(0) == "**":
            parts.append(".*")
        else:
            parts.append("[^/]*")
    parts.append(re.escape(pattern[position:]))
    return re.compile("".join(parts), re.IGNORECASE)


def match(pattern: str, path: str) -> dict[str, str] | None:
    """Return the values captured by pattern on a relative "/"-separated path, or None if it does not match"""
    result = compile_pattern(pattern).fullmatch(path)
    return None if result is None else result.groupdict()
