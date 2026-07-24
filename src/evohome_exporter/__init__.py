#!/usr/bin/env python

import os

from evohomeclient2 import EvohomeClient
from influxdb_client_3 import Point
from schedule import every, repeat
from sentry_sdk import capture_exception

import influxdb_exporter

client = EvohomeClient(
    os.environ.get("EVOHOME_CLIENT_ID"), os.environ.get("EVOHOME_CLIENT_SECRET")
)


def fetch() -> Point:
    points = []

    try:
        for location in client.locations:
            status = location.status()
            for gateway in status["gateways"]:
                for control_system in gateway["temperatureControlSystems"]:
                    for zone in control_system["zones"]:
                        points.append(
                            Point("evohome_v1")
                            .tag("zone", zone["name"])
                            .field(
                                "temperature", zone["temperatureStatus"]["temperature"]
                            )
                            .field(
                                "setpoint",
                                zone["setpointStatus"]["targetHeatTemperature"],
                            )
                            .field("mode", zone["setpointStatus"]["setpointMode"])
                            .field("status", control_system["systemModeStatus"]["mode"])
                        )
    except Exception as e:  # noqa: BLE001
        capture_exception(e)

    return points


@repeat(every().minute)
def evohome_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
