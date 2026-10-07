#!/bin/bash
# run tests for all apps

APPS="main utils events multimedia biblioref leisref institution oer title thesaurus suggest classification error_reporting api"

uv run coverage run manage.py test -v 1 $APPS
uv run coverage report -m
uv run coverage html