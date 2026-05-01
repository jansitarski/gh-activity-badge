"""Tests for badge.config module."""

import os
from unittest.mock import patch

import pytest

from badge.config import Settings, load_settings


class TestLoadSettings:
    @patch.dict(os.environ, {"GITHUB_USERNAME": "testuser", "GITHUB_TOKEN": "tok123"}, clear=True)
    def test_loads_required_vars(self):
        s = load_settings()
        assert s is not None
        assert s.username == "testuser"
        assert s.token == "tok123"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "tok123"}, clear=True)
    def test_missing_username_returns_none(self):
        assert load_settings() is None

    @patch.dict(os.environ, {"GITHUB_USERNAME": "testuser"}, clear=True)
    def test_missing_token_returns_none(self):
        assert load_settings() is None

    @patch.dict(
        os.environ,
        {"INPUT_USERNAME": "inputuser", "INPUT_GITHUB_TOKEN": "inputtok"},
        clear=True,
    )
    def test_input_prefix_fallback(self):
        s = load_settings()
        assert s is not None
        assert s.username == "inputuser"
        assert s.token == "inputtok"

    @patch.dict(
        os.environ,
        {
            "GITHUB_USERNAME": "u",
            "GITHUB_TOKEN": "t",
            "OUTPUT_PATH": "custom.svg",
            "README_UPDATE": "false",
            "README_PATH": "docs/README.md",
            "STATS_START_MARKER": "<!-- BEGIN -->",
            "STATS_END_MARKER": "<!-- END -->",
        },
        clear=True,
    )
    def test_custom_values(self):
        s = load_settings()
        assert s.output_path == "custom.svg"
        assert s.readme_update is False
        assert s.readme_path == "docs/README.md"
        assert s.start_marker == "<!-- BEGIN -->"
        assert s.end_marker == "<!-- END -->"

    @patch.dict(os.environ, {"GITHUB_USERNAME": "u", "GITHUB_TOKEN": "t"}, clear=True)
    def test_defaults(self):
        s = load_settings()
        assert s.output_path == "gh_stats.svg"
        assert s.readme_update is True
        assert s.readme_path == "README.md"


class TestSettings:
    def test_frozen(self):
        s = Settings(
            username="u",
            token="t",
            output_path="o.svg",
            readme_update=True,
            readme_path="R.md",
            start_marker="<!--s-->",
            end_marker="<!--e-->",
        )
        with pytest.raises(AttributeError):
            s.username = "other"


class TestFindRepoRoot:
    def test_finds_git_dir(self, tmp_path):
        (tmp_path / ".git").mkdir()
        nested = tmp_path / "a" / "b" / "c"
        nested.mkdir(parents=True)

        current = nested
        while current != current.parent:
            if (current / ".git").exists():
                assert current == tmp_path
                return
            current = current.parent
        raise AssertionError("Should have found .git")
