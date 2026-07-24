#!/usr/bin/env python

from datetime import UTC, datetime, timedelta

import requests
from influxdb_client_3 import Point
from schedule import every, repeat
from sentry_sdk import capture_exception

import influxdb_exporter


def reqData(
    location: str,
    latitude: float,
    longitude: float,
    today: datetime,
    dayDelta: timedelta,
    yearDelta: int = 0,
) -> Point:
    r"""Request data handler"""
    points = []
    yearInDaysDelta = timedelta(days=365 * yearDelta)
    start = today - yearInDaysDelta

    r = requests.get(
        "https://archive-api.open-meteo.com/v1/archive",
        {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start - dayDelta,
            "end_date": start,
            "models": "best_match",
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "temperature_2m_mean",
                "shortwave_radiation_sum",
            ],
            "timezone": "Europe/Paris",
        },
        timeout=5,
    )
    result = r.json()
    for i in range(len(result["daily"]["time"])):
        if not result["daily"]["temperature_2m_mean"][i]:
            continue
        points.append(
            Point("weather_v2")
            .time(datetime.fromisoformat(result["daily"]["time"][i]) + yearInDaysDelta)
            .tag("year", -yearDelta)
            .tag("location", location)
            .field("temperature_min", result["daily"]["temperature_2m_min"][i])
            .field("temperature_max", result["daily"]["temperature_2m_max"][i])
            .field("temperature_mean", result["daily"]["temperature_2m_mean"][i])
            .field("radiation_sum", result["daily"]["shortwave_radiation_sum"][i])
        )
    return points


def fetch() -> Point:
    today = datetime.now(tz=UTC).date() - timedelta(days=1)
    delta = timedelta(days=7)

    points = []

    try:
        for year in range(3):
            points.extend(
                reqData(
                    location="Paris",
                    latitude=48.83,
                    longitude=2.35,
                    today=today,
                    dayDelta=delta,
                    yearDelta=year,
                )
            )
        points.extend(
            reqData(
                location="Copenhagen",
                latitude=55.68,
                longitude=12.57,
                today=today,
                dayDelta=delta,
            )
        )
    except Exception as e:  # noqa: BLE001
        capture_exception(e)

    return points


@repeat(every(3).hours)
def weather_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
