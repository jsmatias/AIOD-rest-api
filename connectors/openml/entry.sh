#!/bin/bash

# If this directory does not exist, the cron job cannot log (and cannot run)
mkdir -p /opt/connectors/data/openml/dataset
<<<<<<< HEAD
mkdir -p /opt/connectors/data/openml/mlmodel
=======
mkdir -p /opt/connectors/mlmodels/openml/mlmodel
>>>>>>> 1f554a43f3364cad4a5babb681552987571d15b6

# Run cron on the foreground with log level WARN
/usr/sbin/cron -f -l 4
