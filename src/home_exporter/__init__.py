#!/usr/bin/env python

import os
import signal
import sys
from time import sleep

import sentry_sdk
from dotenv import load_dotenv
from schedule import every, repeat, run_pending

load_dotenv()

sentry_sdk.init(
    dsn=os.environ.get("SENTRY_DSN"),
    traces_sample_rate=1.0,
)

import air_exporter  # noqa: F401
import enedis_exporter  # noqa: F401
import evohome_exporter  # noqa: F401
import grdf_exporter  # noqa: F401
import influxdb_exporter
import weather_exporter  # noqa: F401


@repeat(every(3).seconds)
def write_db():
    influxdb_exporter.InfluxDB().write()


def interrupt_handler(signum, frame):
    print(f"Handling signal {signum} ({signal.Signals(signum).name}).")
    influxdb_exporter.InfluxDB().write()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, interrupt_handler)
    while True:
        run_pending()
        sleep(1)


if __name__ == "__main__":
    main()
