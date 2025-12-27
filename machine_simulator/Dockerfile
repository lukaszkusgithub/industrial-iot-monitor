FROM python:3.9-slim

# disable buffering for easier logging
ENV PYTHONUNBUFFERED=1

# directory 
WORKDIR /app

# install required packages
RUN pip install paho-mqtt

# copy source code
COPY main.py .

# start 
CMD ["python", "main.py"]