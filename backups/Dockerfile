FROM ubuntu:latest
FROM python:3.11

COPY backup.sh /opt/backups/scripts/backup.sh
COPY restore.sh /opt/backups/scripts/restore.sh
COPY entry.sh /opt/backups/scripts/entry.sh
COPY entry_restore.sh /opt/backups/scripts/entry_restore.sh
COPY test_backup_restore.py /opt/backups/scripts/test_backup_restore.py
COPY cron /etc/cron.d/backup

USER root
RUN mkdir -p /opt/backups/data/
RUN apt-get update && apt-get install -y cron
RUN pip install pytest==7.4.3
RUN chmod 744 /etc/cron.d/backup
RUN chmod 744 /opt/backups/scripts/backup.sh
RUN chmod 744 /opt/backups/scripts/restore.sh
RUN chmod 744 /opt/backups/scripts/entry.sh
RUN chmod 744 /opt/backups/scripts/entry_restore.sh
RUN crontab /etc/cron.d/backup
