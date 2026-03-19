#!/bin/bash
# run tests for all apps

APPS="main events suggest multimedia biblioref leisref institution oer title
      classification attachments help database text_block thesaurus related
      biremelogin dashboard error_reporting utils api"

for app in $APPS
do
    echo "Running tests from [$app]"
    python -W ignore manage.py test -v 1 $app
done
