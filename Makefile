run:
	pipenv run python manage.py runserver

load:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate

superuser:
	pipenv run python manage.py createsuperuser