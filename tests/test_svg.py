"""Tests for badge.svg module."""

from typing import ClassVar

from badge.svg import render_svg


class TestRenderSvg:
    METRICS: ClassVar[dict[str, int]] = {
        "public_repos": 42,
        "private_repos": 5,
        "contributed_repos": 18,
        "merged_prs": 120,
        "total_commits": 3456,
        "lines_added": 1_500_000,
    }

    def test_returns_valid_svg(self):
        svg = render_svg("testuser", self.METRICS, "2025-01-01")
        assert svg.startswith("<svg")
        assert "</svg>" in svg

    def test_contains_username(self):
        svg = render_svg("octocat", self.METRICS, "2025-01-01")
        assert "octocat" in svg

    def test_contains_formatted_values(self):
        svg = render_svg("u", self.METRICS, "2025-01-01")
        assert "42" in svg  # public_repos
        assert "3,456" in svg  # total_commits with comma
        assert "1.5M" in svg  # lines_added compact

    def test_contains_timestamp(self):
        svg = render_svg("u", self.METRICS, "2025-06-15")
        assert "2025-06-15" in svg

    def test_contains_labels(self):
        svg = render_svg("u", self.METRICS, "2025-01-01")
        assert "Public Repos" in svg
        assert "Merged PRs" in svg
        assert "Lines Added" in svg

    def test_missing_metric_defaults_to_zero(self):
        svg = render_svg("u", {}, "2025-01-01")
        assert "0" in svg

    def test_escapes_username(self):
        svg = render_svg("<bad>", self.METRICS, "2025-01-01")
        assert "<bad>" not in svg
        assert "&lt;bad&gt;" in svg
