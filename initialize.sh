KHUMU_ENVIRONMENT=DEV python manage.py migrate &&
KHUMU_ENVIRONMENT=DEV python manage.py test --keepdb &&
echo "Successfully initialized dev khumu."
