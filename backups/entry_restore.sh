#!/bin/bash

data_to_restore="$1"
cycle="$2"

level=""
backup_path="/opt/backups/data/${data_to_restore}"
destination_path="/opt/data/"

if [ -n "$3" ]; then
    level="-l ${3}"
fi
/bin/bash -c "echo y | /opt/backups/scripts/restore.sh ${backup_path} ${cycle} ${destination_path} ${level}"