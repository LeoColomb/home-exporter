#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date,timedelta,datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client_3 import Point
import influxdb_exporter

from lowatt_grdf.api import API
grdf = API(
    os.environ.get("GRDF_CLIENT_ID"),
    os.environ.get("GRDF_CLIENT_SECRET")
)

def fetch():
    today = date.today() - timedelta(days=1)
    delta = timedelta(days=7)

    points = []

    try:
        for year in range(3):
            start = today - timedelta(days=365 * year)
            for releve in grdf.donnees_consos_informatives(
                os.environ.get("PCE"),
                from_date=(start - delta).isoformat(),
                to_date=(start).isoformat()
            ):
                conso = releve["consommation"]
                points.append(Point("grdf_v2")
                    .time(datetime
                        .fromisoformat(conso["date_fin_consommation"])
                        .replace(year=today.year)
                    )
                    .tag("year", -year)
                    .field("energy", conso["energie"])
                )

    except Exception as e:
        capture_exception(e)

    return points

@repeat(every().day.at("15:05"))
def grdf_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
