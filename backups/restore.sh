#!/bin/bash

BACKUPS_DIR=/opt/backups/data
DESTINATION_DIR=/opt/data
BACKUPS_DIR=../data/backups
DESTINATION_DIR=../data/backups/data
DESTINATION_DIR=../data

data_to_restore=""
backup_cycle=""
level=""

if [ $# -ne 3 ]; then
  echo "Usage: $0 <data_to_restore> <backup_cycle> <sub-level>"
  exit 1
fi

data_to_restore="$1"
backup_cycle="$2"
level="$3"

if ! [[ "$backup_cycle" =~ ^[0-9]+$ ]]; then
    echo "Error: Level must be a non-negative integer: $backup_cycle"
    exit 1
fi
if ! [[ "$level" =~ ^[0-9]+$ ]]; then
    echo "Error: Backup level must be a non-negative integer: $level"
    exit 1
fi

backup_dir="${BACKUPS_DIR}/${data_to_restore}/${data_to_restore}_${backup_cycle}"
if [ ! -d "$backup_dir" ]; then
    echo "Error: Directory does not exist: $backup_dir"
    echo "Operation aborted!"
    exit 1
fi
if [ ! -d "$DESTINATION_DIR" ]; then
    echo "Error: Directory does not exist: $DESTINATION_DIR"
    echo "Operation aborted!"
    exit 1
fi

echo ""
echo "Are you sure you want to proceed? (y/n)"
echo "This overwrites all files and deletes the ones in the destination directory which are not in the archive!"
echo ""
echo "$backup_dir -------> $DESTINATION_DIR/$data_to_restore"

read -r response

case "$response" in
    [yY][eE][sS]|[yY])
        echo "Proceeding..."

        for ((i = 0; i <= level; i++)); do
            backup_file="${backup_dir}/${data_to_restore}${i}.tar.gz"
            if [ ! -f "$backup_file" ]; then
                echo "Error: File does not exist: $backup_file"
                echo "Operation aborted!"
                exit 1
            fi
        done
        
        for ((i = 0; i <= level; i++)); do
            echo "Iteration: $i"
            backup_file="${backup_dir}/${data_to_restore}${i}.tar.gz"
            tar --directory="$DESTINATION_DIR" --extract --file="$backup_file" --listed-incremental=/dev/null
        done
        ;;
    *)
        echo "Operation aborted."
        exit 1
        ;;
esac

echo "Done!"