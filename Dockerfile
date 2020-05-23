FROM python:3.6-alpine
MAINTAINER Guillaume Kulakowski <guillaume@kulakowski.fr>
ENV PS1="\[\e[0;33m\]|> seedboxsync <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt \
    && python setup.py install
WORKDIR /
ENTRYPOINT ["seedboxsync"]
