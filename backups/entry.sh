#!/bin/bash

mkdir -p /opt/backups/data/

# Run cron on the foreground with log level WARN
/usr/sbin/cron -f -l 4