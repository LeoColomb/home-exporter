#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import atexit

import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

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
        self.db = influxdb_client.InfluxDBClient(
        url=os.environ.get("INFLUXDB_URL"),
        token=os.environ.get("INFLUXDB_TOKEN"),
        org=os.environ.get("INFLUXDB_ORG")
        )
        self.write_api = self.db.write_api(write_options=SYNCHRONOUS)
        self.points = []

        atexit.register(self.on_exit)

    def on_exit(self):
        return
        self.write_api.close()
        self.db.close()

    def push(self, points):
        self.points.append(points)

    def write(self):
        if len(self.points) <= 0:
            return
        self.write_api.write(
            bucket=os.environ.get("INFLUXDB_BUCKET"),
            record=self.points
        )
        self.points = []
