FROM python:3.12-slim

RUN apt-get update && apt-get install -y clamav clamav-daemon && apt-get clean

WORKDIR /app
COPY app /app/app
COPY requirements.txt .
COPY clamd.conf /etc/clamav/clamd.conf

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /clamav /defs /var/lib/clamav && chown -R root:root /clamav /defs

EXPOSE 8000

CMD ["bash", "-c", "freshclam && clamd & uvicorn app.main:app --host 0.0.0.0 --port 8000"]
