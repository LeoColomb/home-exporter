#!/usr/bin/env python

import os
from datetime import UTC, datetime, timedelta

from influxdb_client_3 import Point
from lowatt_grdf.api import API
from schedule import every, repeat
from sentry_sdk import capture_exception

import influxdb_exporter

grdf = API(os.environ.get("GRDF_CLIENT_ID"), os.environ.get("GRDF_CLIENT_SECRET"))


def fetch():
    today = datetime.now(tz=UTC).date() - timedelta(days=1)
    delta = timedelta(days=7)

    points = []

    try:
        for year in range(3):
            yearInDaysDelta = timedelta(days=365 * year)
            start = today - yearInDaysDelta
            for releve in grdf.donnees_consos_informatives(
                os.environ.get("PCE"),
                from_date=(start - delta).isoformat(),
                to_date=(start).isoformat(),
            ):
                conso = releve["consommation"]
                points.append(
                    Point("grdf_v3")
                    .time(
                        datetime.fromisoformat(conso["date_fin_consommation"])
                        + yearInDaysDelta
                    )
                    .tag("year", -year)
                    .field("energy", float(conso["energie"]))
                )

    except Exception as e:  # noqa: BLE001
        capture_exception(e)

    return points


@repeat(every().day.at("15:05"))
def grdf_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
