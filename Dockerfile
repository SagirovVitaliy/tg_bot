FROM python:latest

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY ["./source", "/opt/service/"]

RUN chmod +x /opt/service/amqp_service.py && \
    chmod +x /opt/service/bot.py

WORKDIR	/opt/service