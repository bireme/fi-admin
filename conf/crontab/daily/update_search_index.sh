#!/bin/sh
DATE=$(date '+%Y-%m-%d')

cd /app
python manage.py update_search_index --updated_after_days 1 > /logs/update_search_index-${DATE}.log