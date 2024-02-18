FROM ubuntu:latest

COPY backup_data.sh /opt/backups/scripts/backup_data.sh
COPY entry.sh /opt/backups/scripts/entry.sh
COPY cron /etc/cron.d/backup

USER root
RUN chmod 744 /etc/cron.d/backup /opt/backups/scripts/backup_data.sh
RUN chmod +x /opt/backups/scripts/entry.sh
RUN apt-get update && apt-get install -y cron
RUN crontab /etc/cron.d/backup


