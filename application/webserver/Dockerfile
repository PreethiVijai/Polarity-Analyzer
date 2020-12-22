FROM debian:bullseye
RUN apt-get update
RUN apt-get install -y python3 python3-pip
WORKDIR /webserver
# Install python libraries
RUN apt-get update && apt-get install -y git curl default-mysql-client default-libmysqlclient-dev
ADD requirements.txt /webserver/requirements.txt
RUN python3 -m pip install -r requirements.txt
# Upload code
ADD src/* /webserver/

#expose http port
EXPOSE 8080


CMD [ "python3", "webserver.py", "-u" ]