# run tests

echo "Runing tests from [main]"
python manage.py test -v 0 main

echo "Runing tests from [multimedia]"
python manage.py test -v 0 multimedia

