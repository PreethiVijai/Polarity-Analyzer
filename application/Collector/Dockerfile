FROM debian:bullseye
ARG APIKEY
ARG APISECRET
RUN apt-get update
RUN apt-get install -y python3 python3-pip
WORKDIR /Collector
# Install python libraries
ADD requirements.txt /Collector/requirements.txt
RUN python3 -m pip install -r requirements.txt
# Upload code
ADD src/* /Collector/
# RUN echo $APIKEY >> /Collector/apikey.txt
# RUN echo $APISECRET >> /Collector/apisecret.txt
# Expose port to run on
EXPOSE 8080
ENV PYTHONUNBUFFERED 1
CMD python3 Collector.py rabbitmq Covid
