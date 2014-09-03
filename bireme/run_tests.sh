# run tests

echo "Runing tests from [main]"
python manage.py test -v 0 main

echo "Runing tests from [events]"
python manage.py test -v 0 events

echo "Runing tests from [suggest]"
python manage.py test -v 0 suggest

echo "Runing tests from [multimedia]"
python manage.py test -v 0 multimedia
