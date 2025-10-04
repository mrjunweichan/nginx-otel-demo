FROM python:3.11-slim
ARG SERVICE_PATH
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ${SERVICE_PATH}/app.py /app/ 
CMD ["python", "app.py"]
