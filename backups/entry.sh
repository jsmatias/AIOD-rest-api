#!/bin/bash
echo "Running backup and restore tests..."
cd /opt/backups/scripts/
pytest ./test_backup_restore.py

if [ $? -eq 0 ]; then
  echo "Tests passed. Proceeding with regular backup operations."
  /usr/sbin/cron -f
else
  echo "Tests failed. Check the test output for details."
  exit 1
fi
