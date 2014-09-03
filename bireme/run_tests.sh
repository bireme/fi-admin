# run tests

for app in main events suggest multimedia
do
    echo "Runing tests from [$app]"
    python -W ignore manage.py test -v 0 $app
done
