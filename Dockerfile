################################################################################
# Build
#

# ----------------------------------------------------------------- Build assets
FROM node:lts-alpine AS builder-node

WORKDIR /src

COPY . /src
RUN corepack enable && \
    pnpm install --frozen-lockfile && \
    pnpm build


# ------------------------------------------------ Build python and translations
FROM python:3.14-alpine AS builder-python

ENV \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /src
COPY . /src

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

RUN apk add --no-cache just && \
    uv sync --locked && \
    just i18n-compile


################################################################################
# Prod
#
FROM python:3.14-alpine

# -------------------------------------------- Set environment and ARG variables
ENV \
    # Set default PUID / PGUID \
    PUID=1000 \
    PGID=1000 \
    # Setup s6 overlay
    S6_CMD_WAIT_FOR_SERVICES_MAXTIME=0 \
    S6_VERBOSITY=1
ARG \
    # Set version for s6 overlay \
    S6_OVERLAY_VERSION="3.2.3.0" \
    S6_OVERLAY_ARCH="x86_64"

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

# ------------------------------------------------------------ SeedboxSync setup
RUN apk add --update --no-cache shadow su-exec
RUN addgroup -g ${PGID} seedboxsync && adduser -D -u ${PUID} -G seedboxsync seedboxsync

# System folders
RUN mkdir /config && \
    mkdir /downloads && \
    mkdir /watch && \
    mkdir /app && \
    chown -R seedboxsync:seedboxsync /config /downloads /watch

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install app
WORKDIR /app
COPY . /app
RUN uv pip install --system --no-cache-dir -e . && \
    uv pip install --system --no-cache-dir gunicorn && \
    # Cleanup \
    rm -rf /app/docker /app/*.json /app/*.js /app/*.cfg /app/justfile /app/*.lock
COPY --from=builder-node /src/seedboxsync/front/static/dist /app/seedboxsync/front/static/dist
COPY --from=builder-python /src/seedboxsync/front/translations /app/seedboxsync/front/translations

# Seedboxsync folders
RUN chown -R seedboxsync:seedboxsync /app && \
    mkdir /home/seedboxsync/.config && \
    ln -s /config /home/seedboxsync/.config/seedboxsync && \
    ln -s /downloads /home/seedboxsync/downloads && \
    ln -s /watch /home/seedboxsync/watch

# Copy all rootfs files with configuration and others scripts
COPY docker/ /
RUN chmod 755 /etc/s6-overlay/s6-rc.d/*/run && \
    chmod 755 /etc/s6-overlay/s6-rc.d/*/up

# healthcheck
HEALTHCHECK --interval=1m --start-period=1m CMD ["su-exec", "seedboxsync", "seedboxsync", "health"]

WORKDIR /home/seedboxsync
EXPOSE 8000

ENTRYPOINT ["/init"]