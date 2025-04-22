FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "Bionic_50.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
