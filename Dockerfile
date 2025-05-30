################################################################################
# Build
#
FROM python:3.13-alpine as builder

WORKDIR /src

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY . /src
RUN pip install --no-cache-dir cement && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /src/wheels -r requirements.txt && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /src/wheels .



################################################################################
# Prod
#
FROM python:3.13-alpine


# -------------------------------------------- Set environment and ARG variables
ENV \
    # Set default PUID / PGUID \
    PUID=1000 \
    PGID=1000 \
    # Setup s6 overlay
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_VERBOSITY=2
ARG \
    # Set version for s6 overlay \
    ARG S6_OVERLAY_VERSION="3.2.0.2" \
    ARG S6_OVERLAY_ARCH="x86_64"


# ------------------------------------------------------------------- s6 overlay
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz
# Optional symlinks
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-noarch.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-noarch.tar.xz
ADD https://github.com/just-containers/s6-overlay/releases/download/v${S6_OVERLAY_VERSION}/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz /tmp
RUN tar -C / -Jxpf /tmp/s6-overlay-${S6_OVERLAY_ARCH}.tar.xz

RUN apk add --update --no-cache shadow

# ------------------------------------------------------------ SeedboxSync setup
RUN addgroup -g ${PGID} seedboxsync && adduser -D -u ${PUID} -G seedboxsync seedboxsync

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

# Seedboxsync folders
RUN mkdir /home/seedboxsync/.config && \
    ln -s /config /home/seedboxsync/.config/seedboxsync && \
    ln -s /downloads /home/seedboxsync/Downloads && \
    ln -s /watch /home/seedboxsync/watch && \
    cp /usr/local/config/seedboxsync.yml.example /config/seedboxsync.yml

# Copy all rootfs files with configuration and others scripts
COPY docker/ /
RUN chmod 755 /etc/s6-overlay/s6-rc.d/*/run && \
    chmod 755 /etc/s6-overlay/s6-rc.d/*/up

WORKDIR /home/seedboxsync

ENTRYPOINT ["/init"]