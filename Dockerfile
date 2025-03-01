# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

COPY Pipfile Pipfile.lock ./

RUN pip install pipenv && \
      apt-get update && \
      apt-get install -y --no-install-recommends gcc python3-dev libssl-dev build-essential git && \
      pipenv install --deploy --system && \
      apt-get remove -y gcc python3-dev libssl-dev && \
      apt-get autoremove -y && \
      pip uninstall pipenv -y

COPY . ./

# Install production dependencies.
RUN pip3 install .

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
# CMD gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 --worker-class uvicorn.workers.UvicornWorker investmentstk.server:app
CMD uvicorn investmentstk.server:app --host 0.0.0.0 --port $PORT
