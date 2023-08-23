#!/bin/bash

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleExperimentConnector \
  -w /opt/connectors/data/example/experiment

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleMLModelConnector \
  -w /opt/connectors/data/example/ml_model

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleOrganisationConnector \
  -w /opt/connectors/data/example/organisation

python3 connectors/synchronization.py \
  -c connectors.example.example.ExamplePersonConnector \
  -w /opt/connectors/data/example/person

python3 connectors/synchronization.py \
  -c connectors.example.example.ExamplePublicationConnector \
  -w /opt/connectors/data/example/publication

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleServiceConnector \
  -w /opt/connectors/data/example/service
