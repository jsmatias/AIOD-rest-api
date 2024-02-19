FROM ubuntu:latest

COPY backup.sh /opt/backups/scripts/backup.sh
COPY entry.sh /opt/backups/scripts/entry.sh
COPY cron /etc/cron.d/backup

USER root
RUN chmod 744 /etc/cron.d/backup /opt/backups/scripts/backup.sh
RUN chmod +x /opt/backups/scripts/entry.sh
RUN apt-get update && apt-get install -y cron
RUN crontab /etc/cron.d/backup


