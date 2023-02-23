FROM docker.io/alpine:latest as tailscale
WORKDIR /app
# renovate: datasource=github-releases depName=tailscale/tailscale
ARG TAILSCALE_VERSION=v1.36.2
RUN wget https://pkgs.tailscale.com/stable/tailscale_${TAILSCALE_VERSION}_amd64.tgz && \
  tar xzf tailscale_${TAILSCALE_VERSION}_amd64.tgz --strip-components=1

FROM docker.io/python:3 AS builder
WORKDIR /usr/src
ENV PIPENV_VENV_IN_PROJECT=1
RUN pip install --user pipenv
ADD Pipfile.lock Pipfile /usr/src/
RUN /root/.local/bin/pipenv sync

FROM docker.io/python:3
WORKDIR /usr/src/app

RUN mkdir -p \
  /var/run/tailscale \
  /var/cache/tailscale \
  /var/lib/tailscale

RUN apt-get update && apt-get install -y \
    ca-certificates \
    iptables \
  && rm -rf /var/lib/apt/lists/*

COPY --from=tailscale /app/tailscaled /usr/src/app/tailscaled
COPY --from=tailscale /app/tailscale /usr/src/app/tailscale
COPY --from=builder /usr/src/.venv /usr/src/app/.venv
COPY . .

CMD [".fly/start.sh"]
