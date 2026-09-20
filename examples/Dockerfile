FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    "setuptools<81" \
    "nameko==2.14.1" \
    "eventlet==0.40.3" \
    "bottle==0.13.4"

COPY greeting_service.py .
COPY nameko.yaml .

CMD ["nameko", "run", "--config", "nameko.yaml", "greeting_service"]