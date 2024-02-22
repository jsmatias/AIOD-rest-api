import os
import subprocess

from pathlib import Path
from tempfile import TemporaryDirectory

backup_path = Path("./backups").absolute()


def create_test_files(directory: Path, filenames: list):
    """Create test files with simple content."""
    for name in filenames:
        path = directory / name
        with open(path, "w") as f:
            f.write(f"Content of {name}\n")


def test_backup_happy_path():
    """
    "Usage: bash backup.sh <path/to/data> <path/to/backup/dir> <cycle length:int>"
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

        backup_command_list = [
            "bash",
            backup_path / "backup.sh",
            original_dir,
            backup_dir,
            str(cycle_length),
        ]

        for i in range(cycle_length + 1):
            subprocess.run(backup_command_list, check=True)

        for backup_file in files_in_cycle_1 + files_in_cycle_0:
            assert os.path.exists(backup_file)


def test_restore_happy_path():
    """
    "Usage: bash restore.sh backup/path/ <cycle> destination/path/ [--cycle-level <level>]"
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
        backup_command_list = [
            "bash",
            backup_path / "backup.sh",
            original_dir,
            backup_dir,
            str(cycle_length),
        ]
        restore_command_list = [
            "bash",
            backup_path / "restore.sh",
            backup_dir / "original",
            "0",
            restore_dir,
        ]

        subprocess.run(backup_command_list, check=True)
        os.remove(original_dir / "file1.txt")
        subprocess.run(backup_command_list, check=True)

        subprocess.run(restore_command_list, input="y\n", text=True, check=True)
        assert not os.path.exists(restored_file1_path) and os.path.exists(restored_file2_path)

        subprocess.run(
            restore_command_list + ["--cycle-level", "0"], input="y\n", text=True, check=True
        )
        assert os.path.exists(restored_file1_path) and os.path.exists(restored_file2_path)
