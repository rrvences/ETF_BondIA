FROM python:3.12

WORKDIR /app

COPY ./fastapi-app/requirements.txt .

# Copy the pipelines package
COPY pipelines /app/code/pipelines

COPY ./fastapi-app/main.py .

# Set the PYTHONPATH to include the pipelines directory
ENV PYTHONPATH="/app/code/:${PYTHONPATH}"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    apt-get clean

RUN pip install -r requirements.txt

RUN mkdir -p /app/data

RUN mkdir -p /app/data/factsheet

RUN mkdir -p /app/data/json

RUN pip install -r /app/code/pipelines/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]