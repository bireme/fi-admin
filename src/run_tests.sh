#!/bin/bash
# run tests for all apps

APPS="main events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting api"

for app in $APPS
do
    echo "Running tests from [$app]"
    python -W ignore manage.py test -v 1 $app
done

