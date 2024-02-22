#!/bin/bash

# requires tar (GNU tar)

cd ../

env_file=".env"
if [ -f "$env_file" ]; then
  export BACKUPS_PATH=$(grep -m 1 '^BACKUPS_PATH=' "$env_file" | cut -d '=' -f2)
  export DESTINATION_PATH=$(grep -m 1 '^DATA_PATH=' "$env_file" | cut -d '=' -f2)
fi
if [ -z "$BACKUPS_PATH" ] || [ -z "$DESTINATION_PATH" ]; then
  echo "Required environment variables are not set. Check your .env file."
  exit 1
fi

data_to_restore=""
backup_cycle=""
level=""

if [ $# -ne 3 ]; then
  echo "Usage: $0 <data_to_restore> <backup_cycle> <backup_level>"
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

backup_dir="${BACKUPS_PATH}/${data_to_restore}/${data_to_restore}_${backup_cycle}"
if [ ! -d "$backup_dir" ]; then
    echo "Error: Directory does not exist: $backup_dir"
    echo "Operation aborted!"
    exit 1
fi
if [ ! -d "$DESTINATION_PATH" ]; then
    echo "Error: Directory does not exist: $DESTINATION_PATH"
    echo "Operation aborted!"
    exit 1
fi

echo ""
echo "Are you sure you want to proceed? (y/n)"
echo "This overwrites all files and deletes the ones in the destination directory which are not in the archive!"
echo ""
echo "$backup_dir -------> $DESTINATION_PATH/$data_to_restore"

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
            tar --directory="$DESTINATION_PATH" --extract --file="$backup_file" --listed-incremental=/dev/null
        done
        ;;
    *)
        echo "Operation aborted."
        exit 1
        ;;
esac

echo "Done!"