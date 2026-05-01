"""Tests for badge.formatting module."""

from badge.formatting import format_compact, format_number


class TestFormatNumber:
    def test_zero(self):
        assert format_number(0) == "0"

    def test_small(self):
        assert format_number(42) == "42"

    def test_thousands(self):
        assert format_number(1_234) == "1,234"

    def test_millions(self):
        assert format_number(1_234_567) == "1,234,567"

    def test_negative(self):
        assert format_number(-500) == "-500"


class TestFormatCompact:
    def test_below_thousand(self):
        assert format_compact(0) == "0"
        assert format_compact(1) == "1"
        assert format_compact(999) == "999"

    def test_exact_thousand(self):
        assert format_compact(1_000) == "1k"

    def test_thousands_with_decimal(self):
        assert format_compact(1_500) == "1.5k"
        assert format_compact(2_300) == "2.3k"

    def test_thousands_trailing_zero_stripped(self):
        assert format_compact(50_000) == "50k"

    def test_exact_million(self):
        assert format_compact(1_000_000) == "1M"

    def test_millions_with_decimal(self):
        assert format_compact(1_200_000) == "1.2M"

    def test_millions_trailing_zero_stripped(self):
        assert format_compact(5_000_000) == "5M"

    def test_large_millions(self):
        assert format_compact(123_400_000) == "123.4M"
