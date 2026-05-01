"""GitHub API communication layer.

Provides thin wrappers around urllib for both GraphQL and REST endpoints,
plus higher-level functions that orchestrate multiple API calls to collect
all required user metrics.
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, cast

from .config import GRAPHQL_API_URL, PR_ADDITIONS_QUERY, REST_API_URL, STATS_QUERY

USER_AGENT = "github-stats-badge-generator"

MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # seconds; retries at 2s, 4s, 8s

_RETRYABLE_HTTP_CODES = {429, 500, 502, 503, 504}

_TOKEN_PATTERN = re.compile(
    r"(gh[ps]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}|[A-Za-z0-9_]{40})"
)


def _sanitize_error(message: str) -> str:
    """Redact potential tokens/secrets from error messages."""
    return _TOKEN_PATTERN.sub("***REDACTED***", message)


# ---------------------------------------------------------------------------
# Low-level request helpers
# ---------------------------------------------------------------------------


def _request_with_retry(
    request: urllib.request.Request,
    label: str,
) -> str:
    """Execute an HTTP request with retry logic for transient failures.

    Retries on 429, 5xx status codes and connection errors, using
    exponential backoff. Returns the decoded response body.
    """
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body: bytes = response.read()
                return body.decode("utf-8")
        except urllib.error.HTTPError as exc:
            if exc.code not in _RETRYABLE_HTTP_CODES or attempt == MAX_RETRIES - 1:
                error_body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"{label} failed with {exc.code}: {_sanitize_error(error_body)}"
                ) from exc
            last_exc = exc
            wait = RETRY_BACKOFF_BASE * (2**attempt)
            print(
                f"WARNING: {label} returned {exc.code}, retrying in {wait}s "
                f"(attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            time.sleep(wait)
        except (urllib.error.URLError, OSError) as exc:
            if attempt == MAX_RETRIES - 1:
                raise RuntimeError(f"{label} failed: {_sanitize_error(str(exc))}") from exc
            last_exc = exc
            wait = RETRY_BACKOFF_BASE * (2**attempt)
            print(
                f"WARNING: {label} connection error, retrying in {wait}s "
                f"(attempt {attempt + 1}/{MAX_RETRIES})",
                file=sys.stderr,
            )
            time.sleep(wait)

    raise RuntimeError(f"{label} failed after {MAX_RETRIES} retries") from last_exc


def graphql_request(token: str, query: str, variables: dict[str, object]) -> dict[str, object]:
    """Execute a GraphQL query against the GitHub API.

    Raises RuntimeError on HTTP errors, GraphQL errors, or empty responses.
    Retries automatically on transient failures.
    """
    payload = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    request = urllib.request.Request(
        GRAPHQL_API_URL,
        data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )

    body = _request_with_retry(request, "GitHub GraphQL request")

    parsed = json.loads(body)
    if parsed.get("errors"):
        raise RuntimeError(_sanitize_error(json.dumps(parsed["errors"], indent=2)))

    data = parsed.get("data")
    if not data:
        raise RuntimeError(f"No data returned from GitHub GraphQL API: {_sanitize_error(body)}")

    return cast(dict[str, object], data)


def rest_request(token: str, path: str, params: dict[str, str]) -> dict[str, object]:
    """Execute a GET request against the GitHub REST API.

    Raises RuntimeError on HTTP errors or unexpected response formats.
    Retries automatically on transient failures.
    """
    query_string = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{REST_API_URL}{path}?{query_string}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT,
        },
        method="GET",
    )

    body = _request_with_retry(request, f"GitHub REST request ({path})")

    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise RuntimeError("Unexpected REST response payload.")
    return cast(dict[str, object], parsed)


# ---------------------------------------------------------------------------
# Type-checking helpers for API responses
# ---------------------------------------------------------------------------


def require_dict(value: object, path: str) -> dict[str, Any]:
    """Assert that a value is a dict, raising RuntimeError otherwise."""
    if not isinstance(value, dict):
        raise RuntimeError(f"Expected object at {path}, got {type(value).__name__}")
    return cast(dict[str, Any], value)


def require_int(value: object, path: str) -> int:
    """Assert that a value is an int, raising RuntimeError otherwise."""
    if not isinstance(value, int):
        raise RuntimeError(f"Expected integer at {path}, got {type(value).__name__}")
    return value


# ---------------------------------------------------------------------------
# High-level data fetching
# ---------------------------------------------------------------------------


def fetch_pr_additions(
    token: str, username: str, max_pages: int = 100, timeout: float = 300
) -> int:
    """Sum the total lines added across all merged pull requests.

    Paginates through up to `max_pages` pages of 100 PRs each,
    with a brief pause every 10 pages to respect rate limits.
    Stops if `timeout` seconds have elapsed since the call started.
    """
    total = 0
    cursor: str | None = None
    start_time = time.monotonic()

    for page_num in range(max_pages):
        if time.monotonic() - start_time > timeout:
            print(
                f"WARNING: fetch_pr_additions timed out after {timeout}s, results may be incomplete.",
                file=sys.stderr,
            )
            break

        variables: dict[str, object] = {"login": username, "cursor": cursor}
        data = graphql_request(token, PR_ADDITIONS_QUERY, variables)

        user = require_dict(data.get("user"), "data.user")
        prs = require_dict(user.get("pullRequests"), "pullRequests")

        if page_num == 0:
            print(f"Merged PRs to scan: {prs.get('totalCount', '?')}", file=sys.stderr)

        for node in prs.get("nodes") or []:
            if isinstance(node, dict):
                total += node.get("additions", 0)

        page_info = prs.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break

        cursor = page_info.get("endCursor")

        # Rate-limit backoff: pause briefly every 10 pages
        if (page_num + 1) % 10 == 0:
            time.sleep(1)
    else:
        print(
            f"WARNING: Reached max page limit ({max_pages}), results may be incomplete.",
            file=sys.stderr,
        )

    return total


def collect_metrics(username: str, token: str) -> dict[str, int]:
    """Fetch all GitHub metrics for a user.

    Returns a dictionary with keys:
        public_repos, private_repos, merged_prs,
        total_commits, contributed_repos, lines_added
    """
    data = graphql_request(token, STATS_QUERY, {"login": username})
    user = require_dict(data.get("user"), "data.user")

    public_repos = require_int(
        require_dict(user["publicRepositories"], "publicRepositories")["totalCount"],
        "publicRepositories.totalCount",
    )
    private_repos = require_int(
        require_dict(user["privateRepositories"], "privateRepositories")["totalCount"],
        "privateRepositories.totalCount",
    )
    merged_prs = require_int(
        require_dict(user["pullRequests"], "pullRequests")["totalCount"],
        "pullRequests.totalCount",
    )
    contributed_repos = require_int(
        require_dict(user["repositoriesContributedTo"], "repositoriesContributedTo")["totalCount"],
        "repositoriesContributedTo.totalCount",
    )
    print(f"Contributed repos: {contributed_repos}", file=sys.stderr)

    print("Calculating lines added from merged PRs...", file=sys.stderr)
    lines_added = fetch_pr_additions(token, username)
    print(f"Total lines added: {lines_added:,}", file=sys.stderr)

    commits_response = rest_request(token, "/search/commits", {"q": f"author:{username}"})
    total_commits = require_int(
        commits_response.get("total_count"), "rest.search.commits.total_count"
    )

    return {
        "public_repos": public_repos,
        "private_repos": private_repos,
        "merged_prs": merged_prs,
        "total_commits": total_commits,
        "contributed_repos": contributed_repos,
        "lines_added": lines_added,
    }
