#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from time import sleep

import sentry_sdk
from dotenv import load_dotenv
from schedule import run_pending, every, repeat

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
)

import influxdb_exporter # noqa: E402,F401
import grdf_exporter # noqa: E402,F401
import logo_exporter # noqa: E402,F401
import weather_exporter # noqa: E402,F401

@repeat(every(3).seconds)
def write_db():
    influxdb_exporter.InfluxDB().write()

while True:
    run_pending()
    sleep(1)
