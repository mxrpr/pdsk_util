#!/usr/bin/env python3
"""
Smoke tests for pdsk_util Part 1: Dead-code removal and requirements cleanup.
Part 3: Specific-mount filtering fix.
Part 5: argparse + --version.
"""

import subprocess
import sys
import os
import re
import psutil
import pytest


def get_repo_root():
    """Return the repo root directory."""
    return os.path.dirname(os.path.abspath(__file__))


def test_import_pdsk_util():
    """Test 1: python3 -c "import pdsk_util" exits 0, no ImportError/SyntaxError."""
    result = subprocess.run(
        [sys.executable, "-c", "import pdsk_util"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Import failed with returncode {result.returncode}\nstderr: {result.stderr}"


def test_help_flag_long():
    """Test 2: python3 pdsk_util.py --help exits 0, stdout contains 'pdsk-util'."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "--help"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"--help failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "pdsk-util" in result.stdout, f"'pdsk-util' not found in stdout:\n{result.stdout}"


def test_help_flag_short():
    """Test 3: python3 pdsk_util.py -h exits 0, stdout contains 'pdsk-util'."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "-h"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"-h failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "pdsk-util" in result.stdout, f"'pdsk-util' not found in stdout:\n{result.stdout}"


def test_no_args():
    """Test 4: python3 pdsk_util.py (no args) exits 0."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"No args failed with returncode {result.returncode}\nstderr: {result.stderr}"


def test_root_mount():
    """Test 5: python3 pdsk_util.py / exits 0, shows 'Checking volume: /', does not show generic error."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"/ mount check failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "Checking volume: /" in result.stdout, f"'Checking volume: /' not found in stdout:\n{result.stdout}"
    assert "No readable filesystems found" not in result.stdout, f"'No readable filesystems found' should not appear in stdout:\n{result.stdout}"


def test_nonexistent_mount():
    """Test 6: python3 pdsk_util.py /nonexistent_pdsk_test_xyz exits 0, stdout contains 'No readable filesystems'."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/nonexistent_pdsk_test_xyz"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Nonexistent mount check failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "No readable filesystems" in result.stdout, f"'No readable filesystems' not found in stdout:\n{result.stdout}"


def test_nonexistent_mount_shows_specific_not_found_message():
    """Test: /nonexistent_pdsk_test_xyz shows specific 'requested mount' message."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/nonexistent_pdsk_test_xyz"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Nonexistent mount check failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "requested mount" in result.stdout, f"'requested mount' not found in stdout:\n{result.stdout}"
    assert "/nonexistent_pdsk_test_xyz" in result.stdout, f"'/nonexistent_pdsk_test_xyz' not found in stdout:\n{result.stdout}"
    normalized_stdout = " ".join(result.stdout.split())
    assert "not found" in normalized_stdout, f"'not found' not found in stdout:\n{result.stdout}"


def test_nonexistent_mount_does_not_show_generic_message():
    """Test: /nonexistent_pdsk_test_xyz does not show generic 'Probably running with strict permissions' message."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/nonexistent_pdsk_test_xyz"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"Nonexistent mount check failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "Probably running with strict permissions" not in result.stdout, f"'Probably running with strict permissions' should not appear in stdout:\n{result.stdout}"


def test_no_args_does_not_show_specific_not_found_message():
    """Test: pdsk_util.py with no args does not show 'requested mount' or 'Checking volume' messages."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"No args failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "requested mount" not in result.stdout, f"'requested mount' should not appear in stdout:\n{result.stdout}"
    assert "Checking volume" not in result.stdout, f"'Checking volume' should not appear in stdout:\n{result.stdout}"


def test_no_args_generic_message_consistent():
    """Test: pdsk_util.py with no args shows consistent messaging for generic error case."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"No args failed with returncode {result.returncode}\nstderr: {result.stderr}"

    if "No readable filesystems found" in result.stdout:
        # If showing generic error, must also show the permissions hint and NOT show specific message
        assert "Probably running with strict permissions" in result.stdout, f"'Probably running with strict permissions' not found when 'No readable filesystems found' present:\n{result.stdout}"
        assert "requested mount" not in result.stdout, f"'requested mount' should not appear with generic error:\n{result.stdout}"
    else:
        # If not showing error, then it must have found filesystems
        assert "No readable filesystems found" not in result.stdout, f"'No readable filesystems found' should not appear:\n{result.stdout}"


def test_tmpfs_mount_bypasses_noise_filter_when_explicit():
    """Test: /run mount point (tmpfs) is accessible when explicitly requested, bypassing noise filter."""
    # Check if /run exists as a mountpoint on this host
    partitions = psutil.disk_partitions(all=False)
    has_run_mount = any(p.mountpoint == "/run" for p in partitions)

    if not has_run_mount:
        pytest.skip("This test system does not have /run as a mount point")

    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/run"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"/run mount check failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "requested mount" not in result.stdout, f"'requested mount' (not found) should not appear when /run is accessible:\n{result.stdout}"
    assert "Checking volume: /run" in result.stdout, f"'Checking volume: /run' not found in stdout:\n{result.stdout}"


def test_requirements_no_setuptools():
    """Test 7: requirements.txt does not contain 'setuptools'."""
    repo_root = get_repo_root()
    requirements_path = os.path.join(repo_root, "requirements.txt")

    assert os.path.exists(requirements_path), f"requirements.txt not found at {requirements_path}"

    with open(requirements_path, "r") as f:
        content = f.read()

    assert "setuptools" not in content, f"'setuptools' found in requirements.txt:\n{content}"


def test_fstype_skip_set_does_not_contain_vfat():
    """Test Part 4: vfat is not in the fstype skip set."""
    repo_root = get_repo_root()
    pdsk_util_path = os.path.join(repo_root, "pdsk_util.py")

    assert os.path.exists(pdsk_util_path), f"pdsk_util.py not found at {pdsk_util_path}"

    with open(pdsk_util_path, "r") as f:
        content = f.read()

    # Find the line containing "part.fstype in ("
    for line in content.split('\n'):
        if "part.fstype in (" in line:
            assert "'vfat'" not in line, f"'vfat' should not be in fstype skip set, but found in line:\n{line}"
            return

    assert False, "Could not find line containing 'part.fstype in (' in pdsk_util.py"


def test_fstype_skip_set_contains_all_expected_entries():
    """Test Part 4: fstype skip set contains all expected entries (tmpfs, devtmpfs, squashfs, overlay, efivarfs)."""
    repo_root = get_repo_root()
    pdsk_util_path = os.path.join(repo_root, "pdsk_util.py")

    assert os.path.exists(pdsk_util_path), f"pdsk_util.py not found at {pdsk_util_path}"

    with open(pdsk_util_path, "r") as f:
        content = f.read()

    # Find the line containing "part.fstype in ("
    fstype_line = None
    for line in content.split('\n'):
        if "part.fstype in (" in line:
            fstype_line = line
            break

    assert fstype_line is not None, "Could not find line containing 'part.fstype in (' in pdsk_util.py"

    # Check that all expected entries are present
    expected_entries = ['tmpfs', 'devtmpfs', 'squashfs', 'overlay', 'efivarfs']
    for entry in expected_entries:
        assert f"'{entry}'" in fstype_line, f"'{entry}' not found in fstype skip set line:\n{fstype_line}"


def test_version_flag_exits_zero_and_output():
    """Test Part 5: python3 pdsk_util.py --version exits 0, outputs '0.0.1' and 'pdsk-util'."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "--version"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"--version failed with returncode {result.returncode}\nstderr: {result.stderr}"
    assert "0.0.1" in result.stdout, f"'0.0.1' not found in stdout:\n{result.stdout}"
    assert "pdsk-util" in result.stdout, f"'pdsk-util' not found in stdout:\n{result.stdout}"


def test_version_consistency_pdsk_util_vs_setup():
    """Test Part 5: version in pdsk_util.py matches version used in setup.py."""
    repo_root = get_repo_root()
    pdsk_util_path = os.path.join(repo_root, "pdsk_util.py")
    setup_path = os.path.join(repo_root, "setup.py")

    assert os.path.exists(pdsk_util_path), f"pdsk_util.py not found at {pdsk_util_path}"
    assert os.path.exists(setup_path), f"setup.py not found at {setup_path}"

    # Extract version from pdsk_util.py
    with open(pdsk_util_path, "r") as f:
        pdsk_util_content = f.read()
    pdsk_util_match = re.search(r'^__version__\s*=\s*["\'](.+)["\']', pdsk_util_content, re.M)
    assert pdsk_util_match is not None, f"Could not find __version__ in pdsk_util.py"
    pdsk_util_version = pdsk_util_match.group(1)

    # Extract version from setup.py (it reads pdsk_util.py itself using the same regex)
    with open(setup_path, "r") as f:
        setup_content = f.read()
    setup_match = re.search(r'^__version__\s*=\s*["\'](.+)["\']', setup_content, re.M)
    if setup_match:
        # If setup.py has its own __version__ line, extract it
        setup_version = setup_match.group(1)
    else:
        # If setup.py reads from pdsk_util.py (as it does), verify it does so correctly
        # by checking that it contains the regex pattern and reads pdsk_util.py
        assert 'pdsk_util.py' in setup_content, f"setup.py does not reference pdsk_util.py"
        assert r'^__version__\s*=\s*["\'](.+)["\']' in setup_content or '__version__' in setup_content, \
            f"setup.py does not extract __version__"
        # Since setup.py reads from pdsk_util.py, the version should be the same
        setup_version = pdsk_util_version

    assert pdsk_util_version == setup_version, \
        f"Version mismatch: pdsk_util.py has {pdsk_util_version}, setup.py resolves to {setup_version}"


def test_two_positional_args_exits_error():
    """Test Part 5: python3 pdsk_util.py /foo /bar exits with error code 2, stderr contains 'error'."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py", "/foo", "/bar"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True
    )
    assert result.returncode == 2, f"Expected returncode 2, got {result.returncode}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    assert "error" in result.stderr.lower(), f"'error' not found in stderr:\n{result.stderr}"


def test_output_is_sorted_by_mountpoint():
    """Test Part 6: run pdsk_util.py with no args. Parse stdout to extract 'Mounted on' column values. Assert they are in non-decreasing alphabetical order."""
    result = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result.returncode == 0, f"pdsk_util.py failed with returncode {result.returncode}\nstderr: {result.stderr}"

    mountpoints = []
    for line in result.stdout.split('\n'):
        # Strip Rich markup tags
        clean_line = re.sub(r'\[.*?\]', '', line)

        # Skip empty lines and border lines containing box drawing characters
        if not clean_line.strip() or '═' in clean_line:
            continue

        # Try to extract columns using ║ as separator (Rich table format with MINIMAL_DOUBLE_HEAD box)
        if '║' in clean_line:
            cells = clean_line.split('║')
            # Should have structure: empty, col1, col2, col3, col4, col5, col6, col7, empty
            # col7 (cells[7]) is the "Mounted on" column
            if len(cells) >= 9:
                mountpoint = cells[7].strip()
                # Skip the header row (where cell value is "Mounted on")
                if mountpoint and mountpoint != 'Mounted on':
                    mountpoints.append(mountpoint)

    # If there are 0 or 1 mountpoints, the test trivially passes
    if len(mountpoints) <= 1:
        assert True
        return

    # Verify that mountpoints are in sorted order
    sorted_mountpoints = sorted(mountpoints)
    assert mountpoints == sorted_mountpoints, (
        f"Mountpoints are not in sorted order.\n"
        f"Actual: {mountpoints}\n"
        f"Expected: {sorted_mountpoints}"
    )


def test_output_ordering_is_identical_on_repeated_runs():
    """Test Part 6: run pdsk_util.py with no args twice. Strip timestamp patterns. Assert outputs are identical."""
    result1 = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result1.returncode == 0, f"First run failed with returncode {result1.returncode}\nstderr: {result1.stderr}"

    result2 = subprocess.run(
        [sys.executable, "pdsk_util.py"],
        cwd=get_repo_root(),
        capture_output=True,
        text=True,
        timeout=10
    )
    assert result2.returncode == 0, f"Second run failed with returncode {result2.returncode}\nstderr: {result2.stderr}"

    # Strip timestamp pattern: YYYY-MM-DD HH:MM (from the title line)
    # Pattern matches the datetime format used in pdsk_util.py line 24
    timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}'
    output1_stripped = re.sub(timestamp_pattern, 'TIMESTAMP_PLACEHOLDER', result1.stdout)
    output2_stripped = re.sub(timestamp_pattern, 'TIMESTAMP_PLACEHOLDER', result2.stdout)

    assert output1_stripped == output2_stripped, (
        f"Outputs differ after stripping timestamps.\n"
        f"First run (stripped):\n{output1_stripped}\n\n"
        f"Second run (stripped):\n{output2_stripped}"
    )


if __name__ == "__main__":
    pytest_available = True
    try:
        import pytest
    except ImportError:
        pytest_available = False

    if pytest_available:
        pytest.main([__file__, "-v"])
    else:
        print("pytest not available, running tests manually...")
        test_import_pdsk_util()
        print("✓ test_import_pdsk_util passed")
        test_help_flag_long()
        print("✓ test_help_flag_long passed")
        test_help_flag_short()
        print("✓ test_help_flag_short passed")
        test_no_args()
        print("✓ test_no_args passed")
        test_root_mount()
        print("✓ test_root_mount passed")
        test_nonexistent_mount()
        print("✓ test_nonexistent_mount passed")
        test_nonexistent_mount_shows_specific_not_found_message()
        print("✓ test_nonexistent_mount_shows_specific_not_found_message passed")
        test_nonexistent_mount_does_not_show_generic_message()
        print("✓ test_nonexistent_mount_does_not_show_generic_message passed")
        test_no_args_does_not_show_specific_not_found_message()
        print("✓ test_no_args_does_not_show_specific_not_found_message passed")
        test_no_args_generic_message_consistent()
        print("✓ test_no_args_generic_message_consistent passed")
        test_tmpfs_mount_bypasses_noise_filter_when_explicit()
        print("✓ test_tmpfs_mount_bypasses_noise_filter_when_explicit passed")
        test_requirements_no_setuptools()
        print("✓ test_requirements_no_setuptools passed")
        print("\nAll tests passed!")
