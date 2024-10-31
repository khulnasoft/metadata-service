# Use an official Python runtime as a parent image
FROM python:3.11

ARG APP_VERSION

ENV PYTHONPATH=/root \
    PORT=8000 \
    ENV_FOR_DYNACONF=dev-compose \
    PYTHONUNBUFFERED=1 \
    APP_VERSION=${APP_VERSION}

# Set the working directory in the container
WORKDIR /root

COPY requirements.txt .
RUN pip install --no-cache-dir -r /root/requirements.txt

COPY . .

# Make the port available to the world outside this container
EXPOSE ${PORT}

# Run the application
CMD ["python", "./app/main.py"]
