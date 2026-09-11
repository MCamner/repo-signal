"""Keep machine-local filesystem paths out of exported artifacts.

Contract:

    reference = stable logical identity
    not        machine-local physical location

An exported reference identifies the *evidence* — a repository, or a file
within it — never the machine the evidence happened to be produced on.
`/Users/mansys/repo-signal` carries almost no traceability that `repo-signal`
does not, while making the artifact machine-specific and worse to move, compare
or share between runtime environments.

The rule is a shape invariant, deliberately not a fix for one platform: POSIX
absolute paths, Windows drive paths, UNC shares and `~` expansions are all the
same defect wearing different syntax.
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath, PureWindowsPath

# `/x`, `C:\x`, `C:/x`, `\\server\share`, `~/x`, `~user/x`.
_MACHINE_LOCAL = re.compile(r"^(?:/|[A-Za-z]:[\\/]|\\\\|~)")


def is_machine_local_path(value: object) -> bool:
    """True when `value` looks like an absolute machine-local filesystem path."""
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    return bool(_MACHINE_LOCAL.match(text))


def _relative_to(candidate: str, root: str) -> str | None:
    """Return `candidate` relative to `root` as a POSIX path, or None."""
    for flavour in (PurePosixPath, PureWindowsPath):
        try:
            relative = flavour(candidate).relative_to(flavour(root))
        except ValueError:
            continue
        parts = relative.parts
        if not parts:
            return ""
        return "/".join(parts)
    return None


def redact_reference(
    value: object,
    *,
    repo_root: str | object | None,
    repo_name: str,
) -> str:
    """Reduce a reference to logical identity.

    A path inside the repository becomes repository-relative; the repository
    root itself, and anything outside it, becomes the repository name. Values
    that are already logical pass through untouched.
    """
    if not isinstance(value, str) or not value.strip():
        return repo_name
    text = value.strip()

    if not is_machine_local_path(text):
        return text

    if repo_root is not None:
        root = str(repo_root).strip()
        relative = _relative_to(text, root)
        if relative == "":
            return repo_name
        if relative is not None and not is_machine_local_path(relative):
            return relative

    return repo_name
