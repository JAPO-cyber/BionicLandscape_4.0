FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .  
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Avvia streamlit leggendo la porta dinamicamente da Cloud Run
CMD streamlit run Bionic_50.py --server.port=$PORT --server.enableCORS=false --server.enableXsrfProtection=false
