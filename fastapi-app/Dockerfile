FROM python:3.12-slim

# Set environment variables
ENV PYTHONPATH="/app/code:${PYTHONPATH}" \
    PYTHONBUFFERED=1 \
    PIP_NO_CACHE_DIR=1


# 5. Create directories in single layer
RUN mkdir -p /app/data/factsheet

RUN mkdir -p /app/data/json

WORKDIR /app

# 1. Install system dependencies first (better caching)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Copy requirements and install Python dependencies
COPY ./fastapi-app/requirements.txt .
RUN pip install -r requirements.txt

# 3. Copy application files
COPY ./fastapi-app/main.py ./fastapi-app/fastapi_utils.py ./

# 4. Copy pipelines package
COPY pipelines /app/code/pipelines


# 6. Install pipeline requirements if needed (uncomment if required)
COPY pipelines/requirements.txt .
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
