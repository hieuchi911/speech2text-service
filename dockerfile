FROM python:3.8-slim-buster

WORKDIR /python-docker

COPY . .

# Change back to root user to install dependencies
USER root

RUN apt-get update -y && apt-get --yes install libsndfile1 && apt-get --yes install ffmpeg

RUN export TORCH_HUB=./models

RUN pip3 install -r requirements.txt

# By best practices, don't run the code with root user
USER 1001
# fail if run with this user (https://stackoverflow.com/questions/63526148/permissionerror-errno-13-permission-denied-cache-error-occurred-while)

CMD ["sanic", "app:app", "-H", "0.0.0.0", "-p", "5351"]