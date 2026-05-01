"""SVG badge rendering.

Loads Jinja2 templates from the templates/ directory and renders
an animated, dark/light-mode-aware SVG badge displaying GitHub
activity metrics in a 3x2 grid layout.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

from .formatting import format_compact, format_number

# ---------------------------------------------------------------------------
# Template engine setup
# ---------------------------------------------------------------------------

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_env = Environment(
    loader=FileSystemLoader(_TEMPLATE_DIR),
    autoescape=select_autoescape(default_for_string=True, default=True),
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=False,
)

# ---------------------------------------------------------------------------
# Grid layout configuration
# ---------------------------------------------------------------------------

# Grid positions: 3 columns x 2 rows
_GRID_POSITIONS = [
    (0, 0),
    (148, 0),
    (296, 0),  # row 1
    (0, 60),
    (148, 60),
    (296, 60),  # row 2
]

# Ordered list of (metric_key, display_label, use_compact_format)
_METRIC_SLOTS = [
    ("public_repos", "Public Repos", False),
    ("private_repos", "Private Repos", False),
    ("contributed_repos", "Contrib Repos", False),
    ("merged_prs", "Merged PRs", False),
    ("total_commits", "Total Commits", False),
    ("lines_added", "Lines Added", True),
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_svg(
    username: str,
    metrics: dict[str, int],
    generated_at: str,
    *,
    template_name: str = "default.svg.j2",
) -> str:
    """Render a complete SVG badge for the given user metrics.

    Args:
        username: GitHub username (displayed in the title).
        metrics: Dictionary of metric name -> integer value.
        generated_at: Date string shown in the footer timestamp.
        template_name: Jinja2 template file to use (allows future themes).

    Returns:
        Complete SVG document as a string.
    """
    template = _env.get_template(template_name)

    # Build metric cells data for the template loop
    metric_cells = []
    for (x, y), (key, label, compact) in zip(_GRID_POSITIONS, _METRIC_SLOTS):
        raw_value = metrics.get(key, 0)
        formatted = format_compact(raw_value) if compact else format_number(raw_value)
        metric_cells.append({"x": x, "y": y, "value": Markup(formatted), "label": Markup(label)})

    return template.render(
        username=username,
        metrics=metric_cells,
        generated_at=generated_at,
    )
