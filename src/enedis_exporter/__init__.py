#!/usr/bin/env python

import os
from datetime import UTC, datetime, timedelta

from influxdb_client_3 import Point
from schedule import every, repeat
from sentry_sdk import capture_exception

import enedis_exporter.enedis
import influxdb_exporter

enedis = enedis_exporter.enedis.API(
    os.environ.get("ENEDIS_CLIENT_ID"), os.environ.get("ENEDIS_CLIENT_SECRET")
)


def fetch():
    today = datetime.now(tz=UTC).date()

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
            for grandeur in data["grandeur"]:
                for releve in grandeur["points"]:
                    points.append(
                        Point("enedis_v4")
                        .time(datetime.fromisoformat(releve["d"]) + yearInDaysDelta)
                        .tag("year", -year)
                        .tag(
                            "grandeurPhysique",
                            grandeur["grandeurPhysique"],
                        )
                        .tag(
                            "unit",
                            grandeur["unite"],
                        )
                        .field(
                            "value",
                            int(releve["v"]),
                        )
                    )
        # Bi-Hourly
        delta = timedelta(days=2)
        data = enedis.consumption_load_curve(
            os.environ.get("PDL"),
            from_date=(today - delta).isoformat(),
            to_date=(today).isoformat(),
        )
        for grandeur in data["grandeur"]:
            for releve in grandeur["points"]:
                points.append(
                    Point("enedis_hour_v2")
                    .time(datetime.fromisoformat(releve["d"]))
                    .tag(
                        "grandeurPhysique",
                        grandeur["grandeurPhysique"],
                    )
                    .tag(
                        "unit",
                        grandeur["unite"],
                    )
                    .field(
                        "value",
                        int(releve["v"]),
                    )
                )

    except Exception as e:  # noqa: BLE001
        capture_exception(e)

    return points


@repeat(every().day.at("13:37"))
@repeat(every().day.at("01:37"))
def enedis_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
