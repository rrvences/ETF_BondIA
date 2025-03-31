FROM python:3.12

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY BondIA.py .

COPY /pages /app/pages

CMD ["streamlit", "run", "BondIA.py", "--server.port=8501", "--server.address=0.0.0.0"]