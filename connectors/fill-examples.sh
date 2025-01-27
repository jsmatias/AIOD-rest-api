#!/bin/bash

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleCaseStudyConnector \
  -w /opt/connectors/data/example/case_study


python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleComputationalAssetConnector \
  -w /opt/connectors/data/example/computational_asset

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleEducationalResourceConnector \
  -w /opt/connectors/data/example/educational_resource

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleEventConnector \
  -w /opt/connectors/data/example/event

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleExperimentConnector \
  -w /opt/connectors/data/example/experiment

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleMLModelConnector \
  -w /opt/connectors/data/example/ml_model

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleNewsConnector \
  -w /opt/connectors/data/example/news

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleOrganisationConnector \
  -w /opt/connectors/data/example/organisation

python3 connectors/synchronization.py \
  -c connectors.example.example.ExamplePersonConnector \
  -w /opt/connectors/data/example/person

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleProjectConnector \
  -w /opt/connectors/data/example/project

python3 connectors/synchronization.py \
  -c connectors.example.example.ExamplePublicationConnector \
  -w /opt/connectors/data/example/publication

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleServiceConnector \
  -w /opt/connectors/data/example/service

python3 connectors/synchronization.py \
  -c connectors.example.example.ExampleTeamConnector \
  -w /opt/connectors/data/example/team