# Speech-To-Text-Service
Here lives Speech to text service for rasa chatbot at CT Group

## I. Notebook `test-sanic-service.ipynb`:
contains code for:
- testing sanic app that serve speech2text model

## II. Other python files:
contain sanic app that serves speech2text model:
- `app.py` serves nguyenvulebinh/wav2vec-base-vietnamese-250h model
- Before running sanic app:
  - create folders: audio/, facebook-audio/ to store audio downloaded from audio channel (here facebook), and chunks from splitting the audio

To host these sanic services on host machine, execute following command:
  >```
  > python -m sanic <name of file that stores sanic app, e.g if file named app_opus.py, type 'app_opus'>:<name of Sanic object defined in python file> -H <host address> -p <listening port>
  >```

## III. Docker:
- dockerfile in this repo builds docker image that holds environment (requirements.txt) runnable for speech2text service
- docker image: hieuchi911/speech2text-service:without-ckpts
- 2 files are needed to build this image: dockerfile, and `requirements.txt`
- to run the docker service:
  - create folders: audio/, facebook-audio/ to store audio downloaded from audio channel (here facebook), and chunks from splitting the audio
  - run the image, binding the container's working directory with directory containing sanic app file (e.g in this repo, `app.py`).
  - run sanic service in the container (either via `CMD` in dockerfile or provide command at `container run`)
  - these steps is shown in following example:
    >```
    > sudo docker run --name speech2text-service -p 8001:8000 -v "$(pwd):/python-docker/" hieuchi911/speech2text-service:without-ckpts python -m sanic app:app -H 0.0.0.0 -p 8000
    >```
    ,where:
    - `-v "$(pwd)/:/python-docker/"` maps host machine's directory that stores sanic app (`$(pwd)` i.e current folder) with the container's working directory (`/python-docker/`)
    - `python -m sanic app:app -H 0.0.0.0 -p 8000` is the command that run sanic service to listen at port 8000 in the container at container startup. This command is optional since the defined dockerfile already defines this at `CMD` instruction, port specified is 5351 instead of 8000 (the python command in dockerfile wont run since it's overwritten by the python command defined at `docker run`, according to https://docs.docker.com/engine/reference/run/#cmd-default-command-or-options)
    - `-p 8001:8000` maps port `8000` in container to port `8001` in local machine, so requests from outside should be sent to port `8001`
  - Example above corresponds to following docker-compose service block:
    >```
    >speech2text-service:
    >    image: "hieuchi911/speech2text-service:without-ckpts"
    >    expose:
    >       - 8001
    >    volumes:
    >       - $(pwd):/python-docker
    >    command: ["python", "-m", "sanic", "app:app", "-H", "0.0.0.0", "-p", "8000"]
    >```
