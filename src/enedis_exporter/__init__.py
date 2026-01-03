#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from datetime import date, timedelta, datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client_3 import Point
import influxdb_exporter

import enedis_exporter.enedis

enedis = enedis_exporter.enedis.API(
    os.environ.get("ENEDIS_CLIENT_ID"), os.environ.get("ENEDIS_CLIENT_SECRET")
)


def fetch():
    today = date.today()

    points = []

    try:
        # Daily
        delta = timedelta(days=7)
        for year in range(3):
            yearInDaysDelta = timedelta(days=365 * year)
            start = today - yearInDaysDelta
            data = enedis.daily_consumption(
                os.environ.get("PDL"),
                from_date=(start - delta).isoformat(),
                to_date=(start).isoformat(),
            )
            for releve in data["meter_reading"]["interval_reading"]:
                points.append(
                    Point("enedis_v3")
                    .time(datetime.fromisoformat(releve["date"]) + yearInDaysDelta)
                    .tag("year", -year)
                    .field(
                        data["meter_reading"]["reading_type"]["measurement_kind"],
                        int(releve["value"]),
                    )
                )
        # Hourly
        delta = timedelta(days=2)
        data = enedis.consumption_load_curve(
            os.environ.get("PDL"),
            from_date=(today - delta).isoformat(),
            to_date=(today).isoformat(),
        )
        for releve in data["meter_reading"]["interval_reading"]:
            points.append(
                Point("enedis_hour_v1")
                .time(datetime.fromisoformat(releve["date"]))
                .field(
                    data["meter_reading"]["reading_type"]["measurement_kind"],
                    int(releve["value"]),
                )
            )

    except Exception as e:
        capture_exception(e)

    return points


@repeat(every().day.at("13:37"))
@repeat(every().day.at("01:37"))
def enedis_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
