"""
Strict YAML loader for Lane 1 control-plane registry files (L1-004).

A registry file must never parse two ways. This loader rejects, with an
`L-YML-nn` rule id, every construct that makes a control-plane YAML file
ambiguous: duplicate mapping keys, anchors/aliases, merge keys, tabs in
indentation, a leading byte-order mark, multiple YAML documents, a
non-mapping top level, a missing/extra trailing newline, and non-UTF-8
bytes.

Spec: MultiProduct_MasterSpec_v4.0.md Section 5.2; invariants 45, 47.
Task: lanes/L1-05-tasks.md, L1-004.

`load_registry_file` never raises. On any violation it returns
`({}, [Error, ...])`; on success it returns `(parsed_mapping, [])`.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml
from yaml.composer import ComposerError

BOM = b"\xef\xbb\xbf"


@dataclass(frozen=True)
class Error:
    rule_id: str
    message: str


class _AnchorAliasError(Exception):
    """Raised during composition when an anchor or alias is encountered."""


class _MergeKeyError(Exception):
    """Raised during construction when a `<<` merge key is encountered."""


class _DuplicateKeyError(Exception):
    def __init__(self, key, line):
        super().__init__(f"duplicate key '{key}' at line {line}")
        self.key = key
        self.line = line


class _StrictLoader(yaml.SafeLoader):
    """A SafeLoader that refuses anchors, aliases, merge keys and duplicate keys."""


def _compose_node(self, parent, index):
    event = self.peek_event()
    if isinstance(event, yaml.events.AliasEvent):
        raise _AnchorAliasError("alias")
    if getattr(event, "anchor", None):
        raise _AnchorAliasError("anchor")
    return yaml.SafeLoader.compose_node(self, parent, index)


def _flatten_mapping(self, node):
    for key_node, _value_node in node.value:
        if key_node.tag == "tag:yaml.org,2002:merge" or (
            isinstance(key_node.value, str) and key_node.value == "<<"
        ):
            raise _MergeKeyError("<<")
    # No merge keys present — nothing further to flatten.


def _construct_mapping(self, node, deep=False):
    self.flatten_mapping(node)
    mapping = {}
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=deep)
        try:
            hashable = key
            already_present = hashable in mapping
        except TypeError:
            already_present = False
        if already_present:
            raise _DuplicateKeyError(key, key_node.start_mark.line + 1)
        value = self.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


_StrictLoader.compose_node = _compose_node
_StrictLoader.flatten_mapping = _flatten_mapping
_StrictLoader.construct_mapping = _construct_mapping


def _has_tab_in_indentation(text: str) -> int | None:
    """Return the 1-based line number of the first tab found in leading
    whitespace, or None if there is none."""
    for lineno, line in enumerate(text.split("\n"), start=1):
        i = 0
        while i < len(line) and line[i] in (" ", "\t"):
            if line[i] == "\t":
                return lineno
            i += 1
    return None


def load_registry_file(path) -> "tuple[dict, list[Error]]":
    """Load and strictly validate a control-plane registry YAML file.

    Returns (parsed_mapping, []) on success, or ({}, [Error, ...]) on any
    L-YML-01..09 violation. Never raises.
    """
    p = Path(path)

    try:
        raw = p.read_bytes()
    except OSError as e:
        return {}, [Error("L-YML-09", f"could not read file: {e}")]

    # L-YML-05: byte-order mark
    if raw.startswith(BOM):
        return {}, [Error("L-YML-05", "file begins with a byte-order mark")]

    # L-YML-09: non-UTF-8 bytes
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return {}, [Error("L-YML-09", "file is not valid UTF-8")]

    # L-YML-04: tab character in indentation
    bad_line = _has_tab_in_indentation(text)
    if bad_line is not None:
        return {}, [Error("L-YML-04", f"tab in indentation at line {bad_line}")]

    # L-YML-08: file must end with exactly one newline
    if not text.endswith("\n") or text.endswith("\n\n"):
        return {}, [Error("L-YML-08", "file must end with exactly one newline")]

    try:
        loaded = yaml.load(text, Loader=_StrictLoader)
    except _AnchorAliasError:
        return {}, [
            Error("L-YML-02", "anchors and aliases are not permitted in control-plane files")
        ]
    except _MergeKeyError:
        return {}, [Error("L-YML-03", "merge keys are not permitted")]
    except _DuplicateKeyError as e:
        return {}, [Error("L-YML-01", f"duplicate key '{e.key}'")]
    except ComposerError as e:
        if "expected a single document" in str(e):
            return {}, [Error("L-YML-06", "multi-document files are not permitted")]
        return {}, [Error("L-YML-07", f"top level must be a mapping ({e})")]
    except yaml.YAMLError as e:
        return {}, [Error("L-YML-07", f"top level must be a mapping ({e})")]

    if not isinstance(loaded, dict):
        return {}, [Error("L-YML-07", "top level must be a mapping")]

    return loaded, []
