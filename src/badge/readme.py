"""README injection logic.

Handles inserting the generated badge image reference into a README file
between configurable HTML comment markers.
"""

from __future__ import annotations

import sys
from html import escape as html_escape
from pathlib import Path

from .config import REPO_ROOT, Settings


def resolve_safe_path(relative_path: str, label: str) -> Path | None:
    """Resolve a relative path, ensuring it stays within the repository root.

    Returns the resolved Path, or None (with an error printed) if the path
    escapes the repository root.
    """
    resolved = (REPO_ROOT / relative_path).resolve()
    if not str(resolved).startswith(str(REPO_ROOT.resolve())):
        print(f"ERROR: {label} escapes repository root: {relative_path}", file=sys.stderr)
        return None
    return resolved


def update_readme(settings: Settings) -> bool:
    """Inject the badge image tag into the README between markers.

    Returns True on success, False on error. Prints warnings to stderr
    if the README or markers are not found.
    """
    readme_path = resolve_safe_path(settings.readme_path, "README_PATH")
    if readme_path is None:
        return False

    if not readme_path.exists():
        print(f"WARNING: README file not found at {readme_path}", file=sys.stderr)
        print("Skipping README update.", file=sys.stderr)
        return True  # Not a fatal error

    content = readme_path.read_text(encoding="utf-8")

    start_index = content.find(settings.start_marker)
    end_index = content.find(settings.end_marker)

    if start_index == -1 or end_index == -1:
        print(
            f"WARNING: Could not find markers '{settings.start_marker}' and "
            f"'{settings.end_marker}' in {readme_path}",
            file=sys.stderr,
        )
        print(
            "Skipping README update. Add these markers to your README "
            "where you want the badge to appear.",
            file=sys.stderr,
        )
        return True  # Not a fatal error

    escaped_output = html_escape(settings.output_path, quote=True)
    escaped_username = html_escape(settings.username, quote=True)

    injection = (
        f"{settings.start_marker}\n"
        f'<p align="center">\n'
        f'  <img src="./{escaped_output}" alt="{escaped_username}\'s GitHub Stats" />\n'
        f"</p>\n"
        f"{settings.end_marker}"
    )

    new_content = (
        content[:start_index]
        + injection
        + content[end_index + len(settings.end_marker):]
    )

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"Updated {readme_path}", file=sys.stderr)
    return True
