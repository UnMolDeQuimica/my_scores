FROM python:3.12-slim

# Port used by this container to serve HTTP.
EXPOSE 8007

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8007

# Set work directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Run migrations and start server
CMD python manage.py migrate && python manage.py runserver 0.0.0.0:8007