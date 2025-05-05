# Dockerfile

FROM python:3.10-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "scripts/run_single_email.py", "sample_email.json"]
