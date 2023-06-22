#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date,timedelta,datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client import Point
import influxdb_exporter

import enedis_exporter.enedis
enedis = enedis_exporter.enedis.API(
    os.environ.get("ENEDIS_CLIENT_ID"),
    os.environ.get("ENEDIS_CLIENT_SECRET")
)

def fetch():
    today = date.today()

    points = []

    try:
        # Daily
        delta = timedelta(days=7)
        for year in range(3):
            start = today.replace(year=today.year - year)
            data = enedis.daily_consumption(
                os.environ.get("PDL"),
                from_date=(start - delta).isoformat(),
                to_date=(start).isoformat()
            )
            for releve in data["meter_reading"]["interval_reading"]:
                points.append(Point("enedis_v2")
                    .time(datetime.fromisoformat(releve["date"]).replace(year=today.year))
                    .tag("year", start.year)
                    .field(
                        data["meter_reading"]["reading_type"]["measurement_kind"],
                        int(releve["value"])
                    )
                )
        # Hourly
        delta = timedelta(days=1)
        data = enedis.consumption_load_curve(
            os.environ.get("PDL"),
            from_date=(today - delta).isoformat(),
            to_date=(today).isoformat()
        )
        for releve in data["meter_reading"]["interval_reading"]:
            points.append(Point("enedis_hour_v1")
                .time(datetime.fromisoformat(releve["date"]))
                .field(
                    data["meter_reading"]["reading_type"]["measurement_kind"],
                    int(releve["value"])
                )
            )

    except Exception as e:
        capture_exception(e)

    return points

@repeat(every().day.at("13:37"))
def enedis_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
