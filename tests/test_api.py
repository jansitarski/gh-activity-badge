"""Tests for badge.api module — retry logic and helpers."""

import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from badge.api import (
    _request_with_retry,
    graphql_request,
    require_dict,
    require_int,
    rest_request,
)


class TestRequireDict:
    def test_valid_dict(self):
        assert require_dict({"a": 1}, "path") == {"a": 1}

    def test_none_raises(self):
        with pytest.raises(RuntimeError, match=r"data\.user"):
            require_dict(None, "data.user")

    def test_list_raises(self):
        with pytest.raises(RuntimeError):
            require_dict([], "path")


class TestRequireInt:
    def test_valid_int(self):
        assert require_int(42, "path") == 42

    def test_string_raises(self):
        with pytest.raises(RuntimeError, match="path"):
            require_int("42", "path")

    def test_none_raises(self):
        with pytest.raises(RuntimeError):
            require_int(None, "path")


class TestRequestWithRetry:
    def _make_request(self):
        return MagicMock(spec=urllib.request.Request)

    @patch("badge.api.urllib.request.urlopen")
    def test_success_first_try(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"ok": true}'
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = _request_with_retry(self._make_request(), "test")
        assert result == '{"ok": true}'
        assert mock_urlopen.call_count == 1

    @patch("badge.api.time.sleep")
    @patch("badge.api.urllib.request.urlopen")
    def test_retries_on_503(self, mock_urlopen, mock_sleep):
        error_resp = BytesIO(b"server error")
        exc = urllib.error.HTTPError("url", 503, "Service Unavailable", {}, error_resp)

        mock_ok = MagicMock()
        mock_ok.read.return_value = b'{"ok": true}'
        mock_ok.__enter__ = lambda s: s
        mock_ok.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [exc, mock_ok]

        result = _request_with_retry(self._make_request(), "test")
        assert result == '{"ok": true}'
        assert mock_urlopen.call_count == 2
        mock_sleep.assert_called_once_with(2)  # first backoff

    @patch("badge.api.time.sleep")
    @patch("badge.api.urllib.request.urlopen")
    def test_raises_after_max_retries(self, mock_urlopen, mock_sleep):
        def make_error():
            return urllib.error.HTTPError("url", 500, "ISE", {}, BytesIO(b"err"))

        mock_urlopen.side_effect = [make_error(), make_error(), make_error()]

        with pytest.raises(RuntimeError, match="500"):
            _request_with_retry(self._make_request(), "test")
        assert mock_urlopen.call_count == 3

    @patch("badge.api.urllib.request.urlopen")
    def test_no_retry_on_404(self, mock_urlopen):
        exc = urllib.error.HTTPError("url", 404, "Not Found", {}, BytesIO(b"nope"))
        mock_urlopen.side_effect = exc

        with pytest.raises(RuntimeError, match="404"):
            _request_with_retry(self._make_request(), "test")
        assert mock_urlopen.call_count == 1

    @patch("badge.api.time.sleep")
    @patch("badge.api.urllib.request.urlopen")
    def test_retries_on_connection_error(self, mock_urlopen, mock_sleep):
        mock_ok = MagicMock()
        mock_ok.read.return_value = b'{"ok": true}'
        mock_ok.__enter__ = lambda s: s
        mock_ok.__exit__ = MagicMock(return_value=False)

        mock_urlopen.side_effect = [OSError("Connection reset"), mock_ok]

        result = _request_with_retry(self._make_request(), "test")
        assert result == '{"ok": true}'


class TestGraphqlRequest:
    @patch("badge.api._request_with_retry")
    def test_returns_data(self, mock_retry):
        mock_retry.return_value = json.dumps({"data": {"user": {"name": "test"}}})
        result = graphql_request("tok", "query{}", {})
        assert result == {"user": {"name": "test"}}

    @patch("badge.api._request_with_retry")
    def test_raises_on_graphql_errors(self, mock_retry):
        mock_retry.return_value = json.dumps({"errors": [{"message": "bad"}]})
        with pytest.raises(RuntimeError, match="bad"):
            graphql_request("tok", "query{}", {})

    @patch("badge.api._request_with_retry")
    def test_raises_on_empty_data(self, mock_retry):
        mock_retry.return_value = json.dumps({"data": None})
        with pytest.raises(RuntimeError):
            graphql_request("tok", "query{}", {})


class TestRestRequest:
    @patch("badge.api._request_with_retry")
    def test_returns_parsed_dict(self, mock_retry):
        mock_retry.return_value = json.dumps({"total_count": 42})
        result = rest_request("tok", "/search/commits", {"q": "author:test"})
        assert result == {"total_count": 42}

    @patch("badge.api._request_with_retry")
    def test_raises_on_non_dict(self, mock_retry):
        mock_retry.return_value = json.dumps([1, 2, 3])
        with pytest.raises(RuntimeError, match="Unexpected"):
            rest_request("tok", "/path", {})
