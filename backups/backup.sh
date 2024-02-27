#!/bin/bash

if [ $# -ne 3 ]; then
  echo "Usage: $0 path/to/original/ path/to/backup/dir <cycle length:int>"
  echo ""
  echo "Perform incremental backups based on a cycle length."
  echo "A full backup (level 0) is created initially, followed by incremental backups (level 1, 2, ...)."
  echo "These incremental backups contain only the changed files since the last backup."
  echo "The cycle length determines the maximum number of incremental backups before starting a new cycle with a fresh level 0 backup."
  echo "For more details on incremental backups, visit: https://www.gnu.org/software/tar/manual/html_section/Incremental-Dumps.html"
  exit 1
fi

data_path=$(realpath "$1")
data_to_backup=$(basename "$data_path")
backups_path=$(realpath "$2")
cycle_length=$3

another_instance()
{
    echo $(date -u) "This script is already running in a different thread."
    exit 1
}
if [ -n "$RUNNING_UNDER_TEST" ]; then
    echo "Skipping flock in test environment."
else
    exec 9< "$0"
    flock -n -x 9 || another_instance
fi

check_file_or_dir () {
    path=$1
    if [ ! -d "$path" ] && [ ! -f "$path" ]; then
        echo $(date -u) "Error: Path does not exist: $path"
        echo $(date -u) "Operation aborted!"
        exit 1
    fi
}
check_file_or_dir $data_path
check_file_or_dir $backups_path

echo $(date -u) "Backup routine to ${data_to_backup} starting..."

cd "${data_path}"
cd "../"

path_to_backup="./${data_to_backup}"
parent_dir="${backups_path}/${data_to_backup}"

if [ -z "$(ls -A $parent_dir)" ]; then
    backup_dir="${parent_dir}/${data_to_backup}_0"
    mkdir -p "$backup_dir"
    level=0
else
    backup_dir=$(find "$parent_dir" -type d -name "${data_to_backup}*" | sort | tail -n 1)
    level=$(ls "$backup_dir" | grep -c "${data_to_backup}")
    level=$((level - 1))
    if [ $level -le 0 ]; then
        echo $(date -u) "-> Level 0 might be corrupted! Backing up from level 0."
        level=0
    elif [ "$level" -ge "$cycle_length" ]; then
        echo $(date -u) "-> Backup cycle completed, starting a new one."
        last_backup_label="${backup_dir##*_}"
        backup_dir="${parent_dir}/${data_to_backup}_$((last_backup_label + 1))"
        mkdir "$backup_dir"
        level=0
    fi
fi

backup_file="${backup_dir}/${data_to_backup}${level}.tar.gz"
snapshot_file="${backup_dir}/${data_to_backup}.snar"

tar -czf "$backup_file" --listed-incremental="$snapshot_file" "$path_to_backup"

echo $(date -u) "-> Files from ${data_to_backup} backed up."
echo $(date -u) "   ${data_path} -----> ${path_to_backup}"
echo $(date -u) "Done!"

