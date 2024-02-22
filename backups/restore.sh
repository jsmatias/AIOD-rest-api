#!/bin/bash

usage() {
  echo "Usage: $0 backup/path/ <cycle> destination/path/ [--cycle-level <level>]"
  exit 1
}

check_file_or_dir () {
    path=$1
    if [ ! -d "$path" ] && [ ! -f "$path" ]; then
        echo "Error: Path does not exist: $path"
        echo "Operation aborted!"
        exit 1
    fi
}

if [ $# -lt 3 ]; then
  usage
fi

backup_dir=$(realpath "$1")
cycle="$2"
destination_dir=$(realpath "$3")

shift 3 
level=-2

while [ $# -gt 0 ]; do
  case $1 in
    --cycle-level|-cl)
        if [ -n $2 ] && [[ $2 =~ ^[0-9]+$ ]] && [ $2 -ge 0 ]; then
            level="$2"
            shift 2
        else
            echo "Error: --cycle-level|-cl must be followed by a non-negative integer."
            exit 1
        fi
        ;;
    *)
      usage
      ;;
  esac
done

data_to_restore=$(basename "$backup_dir")
backup_dir="${backup_dir}/${data_to_restore}_${cycle}"

check_file_or_dir $backup_dir
check_file_or_dir $destination_dir

echo ""
echo "Are you sure you want to proceed? (y/n)"
echo "This overwrites all files in the destination directory and deletes the ones which are not in the archive!"
echo ""
echo "$backup_dir -------> $destination_dir/$data_to_restore"

read -r response
case "$response" in
    [yY][eE][sS]|[yY])
        echo "Proceeding..."
        concluded=false
        i=0
        while [ "$concluded" = false ]; do
            backup_file="${backup_dir}/${data_to_restore}${i}.tar.gz"
            if [ $i -le $level ] || [ $i -eq 0 ]; then
                check_file_or_dir "$backup_file"
            fi
            if [ $i -eq $((level + 1)) ] || [ ! -f "$backup_file" ]; then
                concluded=true
                level=$((i - 1))
            fi
            i=$((i + 1))
        done
    
        for ((i = 0; i <= level; i++)); do
            backup_file="${data_to_restore}${i}.tar.gz"
            backup_file_path="${backup_dir}/${backup_file}"
            echo "Restoring: $backup_file"
            tar --directory="$destination_dir" --extract --file="$backup_file_path" --listed-incremental=/dev/null
        done
        ;;
    *)
        echo "Operation aborted."
        exit 1
        ;;
esac

echo "Done!"
