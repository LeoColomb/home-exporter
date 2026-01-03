#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client_3 import Point
import influxdb_exporter

import requests


def fetch() -> Point:
    today = date.today()

    cities = [
        {
            "name": "Paris",
            "latitude": 48.83,
            "longitude": 2.35,
        },
        {
            "name": "Copenhagen",
            "latitude": 55.68,
            "longitude": 12.57,
        },
    ]

    points = []

    try:
        for city in cities:
            r = requests.get(
                "https://air-quality-api.open-meteo.com/v1/air-quality",
                {
                    "latitude": city["latitude"],
                    "longitude": city["longitude"],
                    "start_date": today - timedelta(days=1),
                    "end_date": today + timedelta(days=4),
                    "hourly": [
                        "alder_pollen",
                        "birch_pollen",
                        "grass_pollen",
                        "mugwort_pollen",
                        "olive_pollen",
                        "ragweed_pollen",
                        "european_aqi",
                    ],
                    "timezone": "Europe/Paris",
                },
                timeout=5,
            )
            result = r.json()
            for i in range(len(result["hourly"]["time"])):
                points.append(
                    Point("air_v1")
                    .time(datetime.fromisoformat(result["hourly"]["time"][i]))
                    .tag("city", city["name"])
                    .field("european_aqi", result["hourly"]["european_aqi"][i])
                    .field("alder_pollen", result["hourly"]["alder_pollen"][i])
                    .field("birch_pollen", result["hourly"]["birch_pollen"][i])
                    .field("grass_pollen", result["hourly"]["grass_pollen"][i])
                    .field("mugwort_pollen", result["hourly"]["mugwort_pollen"][i])
                    .field("olive_pollen", result["hourly"]["olive_pollen"][i])
                    .field("ragweed_pollen", result["hourly"]["ragweed_pollen"][i])
                )
    except Exception as e:
        capture_exception(e)

    return points


@repeat(every().day.at("10:42"))
def weather_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
