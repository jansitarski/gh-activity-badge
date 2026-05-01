"""Application entry point.

Orchestrates configuration loading, metric collection, SVG generation,
and optional README injection.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone

from .api import collect_metrics
from .config import load_settings
from .readme import resolve_safe_path, update_readme
from .svg import render_svg


def run() -> int:
    """Main application logic. Returns an exit code (0 = success)."""
    settings = load_settings()
    if settings is None:
        return 1

    print(f"Collecting metrics for user: {settings.username}", file=sys.stderr)
    metrics = collect_metrics(settings.username, settings.token)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Render SVG
    svg_content = render_svg(settings.username, metrics, generated_at)

    # Write SVG to disk
    svg_path = resolve_safe_path(settings.output_path, "OUTPUT_PATH")
    if svg_path is None:
        return 1

    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Updated {svg_path}", file=sys.stderr)

    # Optionally update README
    if settings.readme_update:
        if not update_readme(settings):
            return 1

    return 0
