FROM python:3.9-slim

# directory
WORKDIR /app

# install required packages
RUN pip install fastapi uvicorn influxdb-client multipart paho-mqtt


# copy source code
COPY main.py .

# start
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]