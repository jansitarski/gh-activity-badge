"""Tests for badge.readme module."""

from pathlib import Path
from unittest.mock import patch

from badge.config import Settings
from badge.readme import resolve_safe_path, update_readme

FAKE_ROOT = Path("/fake/repo")


def _make_settings(**overrides):
    defaults = dict(
        username="testuser",
        token="fake-token",
        output_path="gh_stats.svg",
        readme_update=True,
        readme_path="README.md",
        start_marker="<!-- stats:start -->",
        end_marker="<!-- stats:end -->",
    )
    defaults.update(overrides)
    return Settings(**defaults)


class TestResolveSafePath:
    @patch("badge.readme.REPO_ROOT", FAKE_ROOT)
    def test_valid_relative_path(self):
        result = resolve_safe_path("README.md", "test")
        assert result is not None
        assert result == (FAKE_ROOT / "README.md").resolve()

    @patch("badge.readme.REPO_ROOT", FAKE_ROOT)
    def test_subdirectory_path(self):
        result = resolve_safe_path("docs/README.md", "test")
        assert result is not None

    @patch("badge.readme.REPO_ROOT", FAKE_ROOT)
    def test_traversal_blocked(self, capsys):
        result = resolve_safe_path("../../etc/passwd", "TEST_PATH")
        assert result is None

    @patch("badge.readme.REPO_ROOT", FAKE_ROOT)
    def test_traversal_blocked_message(self, capsys):
        resolve_safe_path("../../etc/passwd", "TEST_PATH")
        captured = capsys.readouterr()
        assert "ERROR" in captured.err
        assert "TEST_PATH" in captured.err


class TestUpdateReadme:
    def test_injects_badge_between_markers(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text(
            "# Hello\n<!-- stats:start -->\nold content\n<!-- stats:end -->\nfooter\n"
        )
        settings = _make_settings(readme_path="README.md")

        with patch("badge.readme.REPO_ROOT", tmp_path):
            result = update_readme(settings)

        assert result is True
        content = readme.read_text()
        assert '<img src="./gh_stats.svg"' in content
        assert 'alt="testuser\'s GitHub Stats"' in content
        assert "old content" not in content
        assert "footer" in content

    def test_missing_readme_is_not_fatal(self, tmp_path):
        settings = _make_settings(readme_path="NOPE.md")
        with patch("badge.readme.REPO_ROOT", tmp_path):
            result = update_readme(settings)
        assert result is True

    def test_missing_markers_is_not_fatal(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("# Hello\nno markers here\n")
        settings = _make_settings(readme_path="README.md")

        with patch("badge.readme.REPO_ROOT", tmp_path):
            result = update_readme(settings)
        assert result is True
        # Content unchanged
        assert readme.read_text() == "# Hello\nno markers here\n"

    def test_html_escapes_username(self, tmp_path):
        readme = tmp_path / "README.md"
        readme.write_text("<!-- stats:start --><!-- stats:end -->")
        settings = _make_settings(username='<script>alert("xss")</script>')

        with patch("badge.readme.REPO_ROOT", tmp_path):
            update_readme(settings)

        content = readme.read_text()
        assert "<script>" not in content
        assert "&lt;script&gt;" in content
