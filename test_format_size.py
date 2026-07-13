#!/usr/bin/env python3
"""
Unit tests for pdsk_util Part 2: format_size helper function.
"""

import pytest
from pdsk_util import format_size


@pytest.mark.parametrize("bytes_input,expected_output", [
    (0, "0B"),
    (512, "512B"),
    (1023, "1023B"),
    (1024, "1.0K"),
    (1536, "1.5K"),
    (1048576, "1.0M"),  # 1024**2
    (2684354560, "2.5G"),  # int(2.5*1024**3)
    (1099511627776, "1.0T"),  # 1024**4
    (2199023255552, "2.0T"),  # 2*1024**4
    (1099511627775, "1024.0G"),  # 1024**4 - 1
])
def test_format_size(bytes_input, expected_output):
    """Test format_size with various byte values."""
    assert format_size(bytes_input) == expected_output
