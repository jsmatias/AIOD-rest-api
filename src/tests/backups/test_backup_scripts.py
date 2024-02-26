import os
import pytest
import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory

SCRIPTS_PATH = Path("./backups").absolute()


def is_gnu_tar_installed():
    """
    The backup logic requires gnu tar installed.
    """
    try:
        res = subprocess.run(["tar", "--version"], check=True, stdout=subprocess.PIPE)
        return "tar (GNU tar)" in str(res.stdout)
    except subprocess.CalledProcessError:
        return False


pytestmark = pytest.mark.skipif(
    not is_gnu_tar_installed(), reason="It requires GNU tar to run. Skipping all tests."
)


def create_test_files(directory: Path, filenames: list):
    """Create test files with simple content."""
    for name in filenames:
        path = directory / name
        with open(path, "w") as f:
            f.write(f"Content of {name}\n")


def call_backup_command(command: list[str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["RUNNING_UNDER_TEST"] = "1"
    return subprocess.run(command, env=env, check=True)


def call_restore_command(command: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, input="y\n", text=True, check=True)


def test_backup_happy_path():
    """
    Test if the backup.sh script generates the correct directory structure.
    Usage: `bash backup.sh path/to/data path/to/backup/dir <cycle length:int>`
    """
    with TemporaryDirectory() as tmpdir:
        original_dir = tmpdir / Path("original")
        backup_dir = tmpdir / Path("backup")
        os.makedirs(original_dir)
        os.makedirs(backup_dir)
        create_test_files(original_dir, ["file1.txt", "file2.txt"])

        cycle_length = 2
        backup_cycle_0_path = backup_dir / "original" / "original_0"
        backup_cycle_1_path = backup_dir / "original" / "original_1"
        files_in_cycle_0 = [
            backup_cycle_0_path / "original0.tar.gz",
            backup_cycle_0_path / "original1.tar.gz",
            backup_cycle_0_path / "original.snar",
        ]
        files_in_cycle_1 = [
            backup_cycle_1_path / "original0.tar.gz",
            backup_cycle_1_path / "original.snar",
        ]

        backup_command = [
            "bash",
            SCRIPTS_PATH / "backup.sh",
            original_dir,
            backup_dir,
            str(cycle_length),
        ]

        for i in range(cycle_length + 1):
            call_backup_command(backup_command)

        for backup_file in files_in_cycle_1 + files_in_cycle_0:
            assert backup_file.exists()


def test_restore_happy_path():
    """
    Test if the restore.sh script restores the files properly.
    Usage:
    `bash restore.sh \
        backup/path/ <cycle-label:int> destination/path/ [--cycle-level|-cl <level:int>]`
    """
    with TemporaryDirectory() as tmpdir:
        original_dir = tmpdir / Path("original")
        backup_dir = tmpdir / Path("backup")
        restore_dir = tmpdir / Path("restored")
        os.makedirs(original_dir)
        os.makedirs(backup_dir)
        os.makedirs(restore_dir)
        create_test_files(original_dir, ["file1.txt", "file2.txt"])

        restored_file1_path = restore_dir / "original" / "file1.txt"
        restored_file2_path = restore_dir / "original" / "file2.txt"

        cycle_length = 2
        backup_command = [
            "bash",
            SCRIPTS_PATH / "backup.sh",
            original_dir,
            backup_dir,
            str(cycle_length),
        ]
        restore_command = [
            "bash",
            SCRIPTS_PATH / "restore.sh",
            backup_dir / "original",
            "0",
            restore_dir,
        ]

        call_backup_command(backup_command)
        os.remove(original_dir / "file1.txt")
        with open(original_dir / "file2.txt", "w") as f:
            f.write("Content of new file\n")
        call_backup_command(backup_command)

        call_restore_command(restore_command)
        assert not restored_file1_path.exists(), f"{restored_file1_path} shouldn't be here."
        assert restored_file2_path.exists(), f"{restored_file2_path} should be here."

        call_restore_command(restore_command + ["--cycle-level", "0"])
        assert restored_file1_path.exists(), f"{restored_file1_path} should be here."
        assert restored_file2_path.exists(), f"{restored_file2_path} should be here."

        call_restore_command(restore_command + ["-cl", "1"])
        assert not restored_file1_path.exists(), f"{restored_file1_path} shouldn't be here."
        assert restored_file2_path.exists(), f"{restored_file2_path} should be here."
        with open(restored_file2_path, "r") as f:
            file_content = f.read()
        assert "Content of new file\n" in file_content
