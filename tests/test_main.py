"""Tests for badge.main module — orchestrator and entry point."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from badge.main import run


class TestRun:
    """Tests for the run() orchestrator function."""

    @patch("badge.main.load_settings", return_value=None)
    def test_returns_1_when_settings_missing(self, _mock_settings):
        assert run() == 1

    @patch("badge.main.update_readme", return_value=True)
    @patch("badge.main.resolve_safe_path")
    @patch("badge.main.render_svg", return_value="<svg></svg>")
    @patch(
        "badge.main.collect_metrics",
        return_value={
            "public_repos": 10,
            "private_repos": 5,
            "merged_prs": 100,
            "total_commits": 500,
            "contributed_repos": 20,
            "lines_added": 50000,
        },
    )
    @patch("badge.main.load_settings")
    def test_success_writes_svg(
        self, mock_settings, mock_collect, mock_render, mock_safe_path, mock_readme, tmp_path
    ):

        svg_file = tmp_path / "out.svg"
        settings = MagicMock()
        settings.username = "testuser"
        settings.token = "tok"
        settings.output_path = str(svg_file)
        settings.readme_update = False
        mock_settings.return_value = settings
        mock_safe_path.return_value = svg_file

        assert run() == 0

        assert svg_file.exists()
        assert svg_file.read_text() == "<svg></svg>"
        mock_collect.assert_called_once_with("testuser", "tok")

    @patch("badge.main.update_readme", return_value=True)
    @patch("badge.main.resolve_safe_path")
    @patch("badge.main.render_svg", return_value="<svg></svg>")
    @patch(
        "badge.main.collect_metrics",
        return_value={
            "public_repos": 1,
            "private_repos": 0,
            "merged_prs": 0,
            "total_commits": 0,
            "contributed_repos": 0,
            "lines_added": 0,
        },
    )
    @patch("badge.main.load_settings")
    def test_calls_update_readme_when_enabled(
        self, mock_settings, mock_collect, mock_render, mock_safe_path, mock_readme, tmp_path
    ):
        svg_file = tmp_path / "out.svg"
        settings = MagicMock()
        settings.username = "testuser"
        settings.token = "tok"
        settings.output_path = str(svg_file)
        settings.readme_update = True
        mock_settings.return_value = settings
        mock_safe_path.return_value = svg_file

        assert run() == 0
        mock_readme.assert_called_once_with(settings)

    @patch("badge.main.update_readme", return_value=False)
    @patch("badge.main.resolve_safe_path")
    @patch("badge.main.render_svg", return_value="<svg></svg>")
    @patch(
        "badge.main.collect_metrics",
        return_value={
            "public_repos": 1,
            "private_repos": 0,
            "merged_prs": 0,
            "total_commits": 0,
            "contributed_repos": 0,
            "lines_added": 0,
        },
    )
    @patch("badge.main.load_settings")
    def test_returns_1_when_readme_update_fails(
        self, mock_settings, mock_collect, mock_render, mock_safe_path, mock_readme, tmp_path
    ):
        svg_file = tmp_path / "out.svg"
        settings = MagicMock()
        settings.username = "testuser"
        settings.token = "tok"
        settings.output_path = str(svg_file)
        settings.readme_update = True
        mock_settings.return_value = settings
        mock_safe_path.return_value = svg_file

        assert run() == 1


class TestCollectMetrics:
    """Tests for collect_metrics() — the high-level API aggregator."""

    @patch("badge.api.rest_request")
    @patch("badge.api.fetch_pr_additions", return_value=12345)
    @patch("badge.api.graphql_request")
    def test_returns_all_metrics(self, mock_gql, mock_pr_add, mock_rest):
        from badge.api import collect_metrics

        mock_gql.return_value = {
            "user": {
                "publicRepositories": {"totalCount": 10},
                "privateRepositories": {"totalCount": 5},
                "pullRequests": {"totalCount": 42},
                "repositoriesContributedTo": {"totalCount": 20},
            }
        }
        mock_rest.return_value = {"total_count": 999}

        result = collect_metrics("testuser", "tok")

        assert result == {
            "public_repos": 10,
            "private_repos": 5,
            "merged_prs": 42,
            "total_commits": 999,
            "contributed_repos": 20,
            "lines_added": 12345,
        }
        mock_gql.assert_called_once()
        mock_pr_add.assert_called_once_with("tok", "testuser")
        mock_rest.assert_called_once_with("tok", "/search/commits", {"q": "author:testuser"})
