FROM python:3.7.9-alpine

RUN adduser -D microblog

WORKDIR /home/microblog

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN apk add --no-cache --virtual .pynacl_deps build-base python3-dev libffi-dev
RUN python -m pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY microblog.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP microblog.py

RUN chown -R microblog:microblog ./
USER microblog

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]