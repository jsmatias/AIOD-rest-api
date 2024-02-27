#!/bin/bash

usage() {
  echo "Usage: $0 backup/path/ <cycle-label:int> destination/path/ [--level|-l <level:int>]"
  echo ""
  echo "Restores data from incremental backups."
  echo "You must specify name of the data to restore (e.g "connectors") and the cycle label (e.g "1")."
  echo "The cycle label corresponds to the label of the backup directory inside the within the backup path."
  echo "Optionally, you can define a cycle level to restore from a specific incremental backup level within a cycle."
  echo "If the level (-l) option is omitted, all the available levels within the cycle will be restored."
  echo "For more details on the structure and restoration process of incremental backups, visit: https://www.gnu.org/software/tar/manual/html_section/Incremental-Dumps.html"
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
    --level|-l)
        if [ -n $2 ] && [[ $2 =~ ^[0-9]+$ ]] && [ $2 -ge 0 ]; then
            level="$2"
            shift 2
        else
            echo "Error: --level|-l must be followed by a non-negative integer."
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

echo "Restoring process initiated..."

echo "-> Verifying paths..."
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

echo "-> Initiating..."
for ((i = 0; i <= level; i++)); do
    backup_file="${data_to_restore}${i}.tar.gz"
    backup_file_path="${backup_dir}/${backup_file}"
    echo "   Restoring: ${backup_file}"
    tar --directory="$destination_dir" --extract --file="$backup_file_path" --listed-incremental=/dev/null
done
;;
    *)
        echo "Operation aborted."
        exit 1
        ;;
esac

echo "-> Data from backup restored to -------> destination path."
echo "   ${backup_dir} -------> ${destination_dir}${data_to_restore}"
echo "Done!"
