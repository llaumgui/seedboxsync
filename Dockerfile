FROM python:3.12-alpine

LABEL maintainer="Guillaume Kulakowski <guillaume@kulakowski.fr>"
ENV PS1="\[\e[0;33m\]|> seedboxsync <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

# Non root user
RUN adduser -D seedboxsync

WORKDIR /src
COPY . /src

# Add cement for setup.py before
RUN pip install --no-cache-dir cement && \
    # Install SeedboxSync \
    pip install --no-cache-dir . && \
    # Better folder hierarchy \
    mkdir ~seedboxsync/watch && \
    mkdir ~seedboxsync/Downloads && \
    mkdir -p ~seedboxsync/.config/seedboxsync  && \
    cp config/seedboxsync.yml.example ~seedboxsync/.config/seedboxsync/seedboxsync.yml && \
    chown -R seedboxsync:seedboxsync ~seedboxsync && \
    ln -s ~seedboxsync/.config/seedboxsync /config && \
    ln -s ~seedboxsync/watch / && \
    ln -s ~seedboxsync/Downloads /download && \
    # Cleanup \
    rm -rf /src

USER seedboxsync
WORKDIR /home/seedboxsync

ENTRYPOINT ["/usr/local/bin/seedboxsync"]