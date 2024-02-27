# Backup and Restore Process Documentation

This document outlines the process for performing incremental backups and restoring data from these backups. The operations are facilitated through two primary scripts, `backup.sh` for backing up data and `restore.sh` for restoring data. Both scripts are designed to run inside a Docker container, ensuring an isolated and consistent environment for data management. A cron job is configured to schedule backups to different folders inside the storage volume automatically.

## Backup Process

### Script: `backup.sh`

The `backup.sh` script performs [incremental backups](https://www.gnu.org/software/tar/manual/html_section/Incremental-Dumps.html) based on a specified cycle length. An initial full backup (level 0) is created, followed by incremental backups containing only the changes since the last backup. The cycle length determines the number of incremental backups before starting a new cycle with a new level 0 backup.

#### Usage

```bash
./backup.sh path/to/original/ path/to/backup/dir <cycle length:int>
```

Parameters:
- `path/to/original/`: The path to the original data directory you wish to back up.
- `path/to/backup/dir`: The path to the backup directory where the backup files will be stored.
- `<cycle length:int>`: The cycle length indicating the maximum number of incremental backups.

### Scheduling Backups

Backups are scheduled using a cron job inside the container. The cron job is configured to execute the `backup.sh` script at specified intervals, ensuring regular backups to different folders within the storage volume.

## Restore Process

### Script: `restore.sh`

The `restore.sh` script allows for the restoration of data from the incremental backups. It requires specifying the data to restore and the cycle label of the backup. Optionally, a specific incremental backup level within a cycle can be defined for restoration.

#### Usage

```bash
./restore.sh backup/path/ <cycle-label:int> destination/path/ [--level|-l <level:int>]
```

Parameters:
- `backup/path`: Path of the backed up data to be restored.
- `<cycle-label:int>`: The label of the backup directory within the backup path.
- `destination/path`: Path to the destination folder.
- `--level|-l <level:int>`: (Optional) The specific incremental backup level within a cycle to restore from.

## Container Setup

### Entry File

An entry file is executed at container startup to perform a quick health check of the backup and restore scripts. This ensures the scripts are functioning correctly before proceeding with regular backups.

### Manual Restoration

To manually restore data, stop the container and replace the command in the Docker Compose file to call the `entry_restore.sh` script with appropriate parameters.

#### Docker Compose Example

```yaml
services:
  backup:
    image: aiod-backup
    volumes:
      - ./backups:/opt/backups/scripts
      - /path/to/backups:/opt/backups/data
      - /path/to/connectors/data/:/opt/data/connectors 
    command: /bin/bash -c "/opt/backups/scripts/entry.sh"
    # Replace the above command with the following to initiate restoration of the connectors volume from cycle 2 and level 10:
    # command: /bin/bash -c "/opt/backups/scripts/entry_restore.sh connectors 2 10"
```