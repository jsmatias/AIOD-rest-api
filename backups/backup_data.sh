#!/bin/bash

BACKUP_DIR=/opt/backups/data/
CONNECTORS_DIR=/opt/data/

another_instance()
{
    echo $(date -u) "This script is already running in a different thread."
    exit 1
}
exec 9< "$0"
flock -n -x 9 || another_instance

echo $(date -u) "Backup service starting..."

cd ${CONNECTORS_DIR}

tar -czf ${BACKUP_DIR}/connectors.tar.gz connectors
echo $(date -u) "Connectors state and logs done."

tar -czf ${BACKUP_DIR}/deletion.tar.gz deletion
echo $(date -u) "Deletion state and logs done."

tar -czf ${BACKUP_DIR}/elasticsearch.tar.gz elasticsearch
echo $(date -u) "Elastic Search state and logs done."

tar -czf ${BACKUP_DIR}/keycloak.tar.gz keycloak
echo $(date -u) "Keycloak db done."

tar -czf ${BACKUP_DIR}/mysql.tar.gz mysql
echo $(date -u) "MySQL db done."

echo $(date -u) "Backup completed!"