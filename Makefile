.PHONY: setup_and_run load superuser run

setup_and_run: load superuser run

run:
	pipenv run python manage.py runserver 0.0.0.0:8000

load:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate

superuser:
	pipenv run python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"
