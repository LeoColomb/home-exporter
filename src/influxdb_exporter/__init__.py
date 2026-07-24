#!/usr/bin/env python

import atexit
import os

from influxdb_client_3 import SYNCHRONOUS, InfluxDBClient3, write_client_options
from sentry_sdk import capture_exception


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class InfluxDB:
    def __init__(self) -> None:
        self.db = InfluxDBClient3(
            host=os.environ.get("INFLUXDB_URL"),
            token=os.environ.get("INFLUXDB_TOKEN"),
            org=os.environ.get("INFLUXDB_ORG"),
            database=os.environ.get("INFLUXDB_BUCKET"),
            write_client_options=write_client_options(write_options=SYNCHRONOUS),
        )
        self.points = []

        atexit.register(self.on_exit)

    def on_exit(self):
        self.write()
        self.db.close()

    def push(self, points):
        self.points.append(points)

    def write(self):
        if len(self.points) <= 0:
            return
        try:
            self.db.write(record=self.points)
            self.points.clear()
        except Exception as e:  # noqa: BLE001
            capture_exception(e)
