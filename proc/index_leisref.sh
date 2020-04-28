export PYTHONWARNINGS="ignore::DeprecationWarning"
source /home/apps/bvsalud-org/fi-admin/env/bin/activate

python manage.py shell < index_leisref.py

