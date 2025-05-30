FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y wget unzip \
 && playwright install chromium

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
