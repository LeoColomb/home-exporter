#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client_3 import Point
import influxdb_exporter

from evohomeclient2 import EvohomeClient
client = EvohomeClient(
    os.environ.get("EVOHOME_CLIENT_ID"),
    os.environ.get("EVOHOME_CLIENT_SECRET")
)

def fetch() -> Point:
    points = []

    try:
        for device in client.temperatures():
            points.append(Point("evohome_v1")
                .tag('zone', device['name'])
                .field('temperature', device['temp'])
            )
        # for location in client.locations:
        #     for zone in location._gateways[0]._control_systems[0].zones:
    except Exception as e:
        capture_exception(e)

    return points

@repeat(every().minute)
def evohome_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
