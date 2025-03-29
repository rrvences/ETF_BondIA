FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the ai_processing package
COPY ../processing /app/processing

RUN pip install -r /app/processing/requirements.txt


COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]