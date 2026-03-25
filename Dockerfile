FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

# Create directories for persistent data and static files
RUN mkdir -p /code/db /code/staticfiles /code/media

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8007

CMD python manage.py migrate && gunicorn scoremanager.wsgi:application --bind 0.0.0.0:8007 --workers 3
