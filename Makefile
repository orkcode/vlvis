.PHONY: run load superuser

run:
    pipenv run python manage.py runserver 0.0.0.0:8000

load:
    pipenv run python manage.py makemigrations
    pipenv run python manage.py migrate

superuser:
    pipenv run python manage.py createsuperuser
