#!/bin/bash

BACKUPS_PATH=/opt/backups/data
DATA_PATH=/opt/data
BACKUP_CYCLE=7

another_instance()
{
    echo $(date -u) "This script is already running in a different thread."
    exit 1
}
exec 9< "$0"
flock -n -x 9 || another_instance


cd "$DATA_PATH"

function backup_data {
    data_to_backup=$1
    path_to_bkp="${data_to_backup}"
    parent_dir="${BACKUPS_PATH}/${data_to_backup}"

    if [ -z "$(ls -A $parent_dir)" ]; then
        backup_dir="${parent_dir}/${data_to_backup}_0"
        mkdir -p "$backup_dir"
        level=0
    else
        backup_dir=$(find "$parent_dir" -type d -name "${data_to_backup}*" | sort | tail -n 1)
        level=$(ls "$backup_dir" | grep -c "${data_to_backup}")
        level=$((level - 1))
        if [ $level -le 0 ]; then
            echo "Level 0 might be corrupted! Backing up from level 0."
            level=0
        elif [ "$level" -ge "$BACKUP_CYCLE" ]; then
            echo "Backup cycle completed, starting a new one."
            last_backup_label="${backup_dir##*_}"
            backup_dir="${parent_dir}/${data_to_backup}_$((last_backup_label + 1))"
            mkdir "$backup_dir"
            level=0
        fi
    fi

    backup_file="${backup_dir}/${data_to_backup}${level}.tar.gz"
    snapshot_file="${backup_dir}/${data_to_backup}.snar"

    tar -czf "$backup_file" --listed-incremental="$snapshot_file" "$path_to_bkp"
    echo $(date -u) "$data_to_backup done..."
}

echo $(date -u) "Backup routine starting..."

backup_data "connectors"
backup_data "keycloak"
backup_data "deletion"
backup_data "elasticsearch"
backup_data "mysql"

echo $(date -u) "Backup completed!"
