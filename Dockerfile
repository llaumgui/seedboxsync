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
    # System folders \
    mkdir /config && \
    mkdir /download && \
    mkdir /watch && \
    chown -R seedboxsync:seedboxsync /config /download /watch && \
    # Seedboxsync folders
    mkdir ~seedboxsync/.config && \
    ln -s /config ~seedboxsync/.config/seedboxsync && \
    ln -s /download ~seedboxsync/Downloads && \
    ln -s /watch ~seedboxsync/watch && \
    cp config/seedboxsync.yml.example /config/seedboxsync.yml && \
    chown -R seedboxsync:seedboxsync ~seedboxsync/.config && \
    # Cleanup \
    rm -rf /src

USER seedboxsync
WORKDIR /home/seedboxsync

ENTRYPOINT ["/usr/local/bin/seedboxsync"]