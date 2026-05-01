"""Number formatting utilities."""

from __future__ import annotations


def format_number(value: int) -> str:
    """Format an integer with comma separators (e.g. 1,234,567)."""
    return f"{value:,}"


def format_compact(value: int) -> str:
    """Format a number in compact human-readable form (e.g. 50k, 1.2M).

    Values below 1,000 are returned as-is.
    """
    if value >= 1_000_000:
        raw = f"{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        raw = f"{value / 1_000:.1f}k"
    else:
        return str(value)

    # Strip trailing ".0" before the suffix: "50.0k" -> "50k"
    suffix = raw[-1]
    num_part = raw[:-1]
    if "." in num_part:
        num_part = num_part.rstrip("0").rstrip(".")
    return num_part + suffix
