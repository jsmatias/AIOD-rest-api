FROM ubuntu:latest

COPY backup.sh /opt/backups/scripts/backup.sh
COPY cron /etc/cron.d/backup

USER root
RUN mkdir -p /opt/backups/data/
RUN chmod 744 /etc/cron.d/backup 
RUN chmod 744 /opt/backups/scripts/backup.sh
RUN apt-get update && apt-get install -y cron
RUN crontab /etc/cron.d/backup
