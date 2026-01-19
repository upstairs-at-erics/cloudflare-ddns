FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir requests

COPY ddns-cloudflare.py /app/ddns-cloudflare.py

CMD ["sh", "-c", "while true; do python3 -u /app/ddns-cloudflare.py; sleep 600; done"]
