"""Configuration and constants.

Centralizes all environment variable reading, default values,
API endpoints, and GraphQL query definitions.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

GRAPHQL_API_URL = "https://api.github.com/graphql"
REST_API_URL = "https://api.github.com"

# ---------------------------------------------------------------------------
# Project Paths
# ---------------------------------------------------------------------------


def _find_repo_root() -> Path:
    """Return the repository / workspace root.

    Prefers the GITHUB_WORKSPACE environment variable (always set inside
    GitHub Actions) so that the path is correct even when the package is
    pip-installed into site-packages.  Falls back to walking up from the
    current working directory, then from this source file.
    """
    # 1. Explicit env var (GitHub Actions always sets this)
    env_root = os.environ.get("GITHUB_WORKSPACE")
    if env_root:
        return Path(env_root)

    # 2. Walk up from cwd (works for local invocations)
    current = Path.cwd().resolve()
    while current != current.parent:
        if (current / ".git").exists() or (current / "action.yml").exists():
            return current
        current = current.parent

    # 3. Fallback to cwd itself
    return Path.cwd().resolve()


REPO_ROOT = _find_repo_root()

# ---------------------------------------------------------------------------
# GraphQL Queries
# ---------------------------------------------------------------------------

STATS_QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER) {
      totalCount
    }
    publicRepositories: repositories(ownerAffiliations: OWNER, privacy: PUBLIC) {
      totalCount
    }
    privateRepositories: repositories(ownerAffiliations: OWNER, privacy: PRIVATE) {
      totalCount
    }
    pullRequests(states: MERGED) {
      totalCount
    }
    repositoriesContributedTo(
      contributionTypes: [COMMIT, PULL_REQUEST, PULL_REQUEST_REVIEW]
      includeUserRepositories: true
      first: 1
    ) {
      totalCount
    }
  }
}
""".strip()

PR_ADDITIONS_QUERY = """
query($login: String!, $cursor: String) {
  user(login: $login) {
    pullRequests(states: MERGED, first: 100, after: $cursor) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        additions
      }
    }
  }
}
""".strip()

# ---------------------------------------------------------------------------
# Runtime Configuration (read from environment)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Settings:
    """Immutable application settings parsed from environment variables."""

    username: str
    token: str
    output_path: str
    readme_update: bool
    readme_path: str
    start_marker: str
    end_marker: str


def load_settings() -> Settings | None:
    """Load settings from environment variables.

    Returns None if required variables (username, token) are missing.
    Prints error messages to stderr for missing required values.
    """
    import sys

    username = os.environ.get("GITHUB_USERNAME") or os.environ.get("INPUT_USERNAME")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("INPUT_GITHUB_TOKEN")

    if not username:
        print(
            "ERROR: GITHUB_USERNAME (or INPUT_USERNAME) environment variable is required.",
            file=sys.stderr,
        )
        return None

    if not token:
        print(
            "ERROR: GITHUB_TOKEN (or INPUT_GITHUB_TOKEN) environment variable is required. "
            "Provide a token with 'repo' and 'read:user' scopes.",
            file=sys.stderr,
        )
        return None

    output_path = os.environ.get("OUTPUT_PATH") or os.environ.get(
        "INPUT_OUTPUT_PATH", "gh_stats.svg"
    )
    readme_update = (
        os.environ.get("README_UPDATE") or os.environ.get("INPUT_README_UPDATE", "true")
    ).lower() == "true"
    readme_path = os.environ.get("README_PATH") or os.environ.get("INPUT_README_PATH", "README.md")
    start_marker = os.environ.get("STATS_START_MARKER") or os.environ.get(
        "INPUT_STATS_START_MARKER", "<!-- stats:start -->"
    )
    end_marker = os.environ.get("STATS_END_MARKER") or os.environ.get(
        "INPUT_STATS_END_MARKER", "<!-- stats:end -->"
    )

    return Settings(
        username=username,
        token=token,
        output_path=output_path,
        readme_update=readme_update,
        readme_path=readme_path,
        start_marker=start_marker,
        end_marker=end_marker,
    )
