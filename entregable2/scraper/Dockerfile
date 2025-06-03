# scraper/Dockerfile

FROM python:3.8-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY scraper.py /app/

RUN pip install --no-cache-dir requests pymongo

CMD ["python", "scraper.py"]
