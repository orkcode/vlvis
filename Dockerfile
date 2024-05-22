FROM python:3.11-slim-buster

RUN apt-get update && apt-get upgrade -y

ENV APP_ROOT /app
WORKDIR ${APP_ROOT}

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --deploy --ignore-pipfile

COPY . ${APP_ROOT}

CMD ["gunicorn", "-c", "gunicorn.conf.py", "config.wsgi:application"]
