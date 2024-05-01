#
# Build
#
FROM python:3.12-alpine as builder

WORKDIR /src

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . /src
RUN pip install --no-cache-dir cement && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /src/wheels -r requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /src/wheels .



#
# Prod
#
FROM python:3.12-alpine

# Non root user
RUN adduser -D seedboxsync

WORKDIR /src

# System folders
RUN mkdir /config && \
    mkdir /downloads && \
    mkdir /watch && \
    chown -R seedboxsync:seedboxsync /config /downloads /watch

# Add cement for setup.py before
COPY --from=builder /src/wheels wheels
RUN pip install --no-cache-dir wheels/* && \
    rm -rf /src

USER seedboxsync
# Seedboxsync folders
RUN mkdir ~seedboxsync/.config && \
    ln -s /config ~seedboxsync/.config/seedboxsync && \
    ln -s /downloads ~seedboxsync/Downloads && \
    ln -s /watch ~seedboxsync/watch && \
    cp /usr/local/config/seedboxsync.yml.example /config/seedboxsync.yml

WORKDIR /home/seedboxsync

ENTRYPOINT ["/usr/local/bin/seedboxsync"]