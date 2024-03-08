"""
These tests are meant to be run from the host server,
prior to the execution of the backup.sh and restore.sh scripts.
"""

import os
import pytest
import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory


def is_gnu_tar_installed():
    try:
        result = subprocess.run(
            ["tar", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return "GNU tar" in result.stdout
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_gnu_tar_installed(), reason="backup.sh and restore.sh require GNU tar to be installed."
)

SCRIPTS_PATH = Path(__file__).resolve().parent.parent.parent.parent / "scripts"


def create_test_files(directory: Path, filenames: list):
    """Create test files with simple content."""
    for name in filenames:
        path = directory / name
        with open(path, "w") as f:
            f.write(f"Content of {name}\n")


def call_backup_command(command: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(command, env=env, check=True)


def call_restore_command(command: list[str], env: dict) -> subprocess.CompletedProcess:
    return subprocess.run(command, env=env, input="y\n", text=True, check=True)


def test_backup_happy_path():
    """
    Test if the backup.sh script generates the correct directory structure.
    Usage: `bash backup.sh <data to backup:str> <cycle length:int>`
    """
    with TemporaryDirectory() as tmpdir:
        cycle_length = 2
        data_name = "original"

        data_dir = tmpdir / Path("data")
        original_dir = tmpdir / Path("data") / data_name
        backup_dir = tmpdir / Path("backups")
        env = os.environ.copy()
        env["ENV_MODE"] = "testing"
        env["DATA_PATH"] = str(data_dir)
        env["BACKUP_PATH"] = str(backup_dir)

        os.makedirs(original_dir)
        os.makedirs(backup_dir)
        create_test_files(original_dir, ["file1.txt", "file2.txt"])

        backup_cycle_0_path = backup_dir / data_name / f"{data_name}_0"
        backup_cycle_1_path = backup_dir / data_name / f"{data_name}_1"
        files_in_cycle_0 = [
            backup_cycle_0_path / f"{data_name}0.tar.gz",
            backup_cycle_0_path / f"{data_name}1.tar.gz",
            backup_cycle_0_path / f"{data_name}.snar",
        ]
        files_in_cycle_1 = [
            backup_cycle_1_path / f"{data_name}0.tar.gz",
            backup_cycle_1_path / f"{data_name}.snar",
        ]

        backup_command = ["bash", SCRIPTS_PATH / "backup.sh", data_name, str(cycle_length)]

        for i in range(cycle_length + 1):
            call_backup_command(backup_command, env)

        for backup_file in files_in_cycle_1 + files_in_cycle_0:
            assert backup_file.exists()


def test_restore_happy_path():
    """
    Test if the restore.sh script restores the files properly.
    Usage:
    `bash restore.sh <data to restore:str> <cycle label:int> [--level|-l <level:int>]`
    """
    with TemporaryDirectory() as tmpdir:
        cycle_length = 2
        data_name = "original"

        data_dir = tmpdir / Path("data")
        original_dir = tmpdir / Path("data") / data_name
        backup_dir = tmpdir / Path("backups")
        env = os.environ.copy()
        env["ENV_MODE"] = "testing"
        env["DATA_PATH"] = str(data_dir)
        env["BACKUP_PATH"] = str(backup_dir)

        os.makedirs(original_dir)
        os.makedirs(backup_dir)
        create_test_files(original_dir, ["file1.txt", "file2.txt"])

        restored_file1_path = original_dir / "file1.txt"
        restored_file2_path = original_dir / "file2.txt"

        backup_command = ["bash", SCRIPTS_PATH / "backup.sh", data_name, str(cycle_length)]
        restore_command = ["bash", SCRIPTS_PATH / "restore.sh", data_name, "0"]

        call_backup_command(backup_command, env)
        os.remove(original_dir / "file1.txt")
        with open(original_dir / "file2.txt", "w") as f:
            f.write("Content of new file\n")
        call_backup_command(backup_command, env)

        call_restore_command(restore_command, env)
        assert not restored_file1_path.exists(), f"{restored_file1_path} shouldn't be here."
        assert restored_file2_path.exists(), f"{restored_file2_path} should be here."
        with open(restored_file2_path, "r") as f:
            file_content = f.read()
        assert "Content of new file\n" in file_content

        call_restore_command(restore_command + ["--level", "0"], env)
        assert restored_file1_path.exists(), f"{restored_file1_path} should be here."
        assert restored_file2_path.exists(), f"{restored_file2_path} should be here."

        call_restore_command(restore_command + ["-l", "1"], env)
        assert not restored_file1_path.exists(), f"{restored_file1_path} shouldn't be here."
