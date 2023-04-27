FROM docker.io/tailscale/tailscale:v1.40.0 as tailscale

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

COPY --from=tailscale /usr/local/bin/tailscaled /usr/src/app/tailscaled
COPY --from=tailscale /usr/local/bin/tailscale /usr/src/app/tailscale
COPY --from=builder /usr/src/.venv /usr/src/app/.venv
COPY . .

CMD [".fly/start.sh"]
