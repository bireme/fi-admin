#!/bin/bash
# run tests for all apps

APPS="main events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting"

coverage run manage.py test -v 1 $APPS
coverage report -m
coverage html