#!/bin/sh

# Run Tailscale
/usr/src/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
sleep 2
/usr/src/app/tailscale up --authkey="${TAILSCALE_AUTHKEY}" --hostname=fly-home-exporter --accept-routes

# Run exporter
/usr/src/app/.venv/bin/python /usr/src/app/main.py
