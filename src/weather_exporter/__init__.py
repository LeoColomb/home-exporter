#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import date, timedelta, datetime

from schedule import every, repeat
from sentry_sdk import capture_exception
from influxdb_client_3 import Point
import influxdb_exporter

import requests

def hdd(Tn: float, Tx: float, Tmoy: float, Tref: float=17.0) -> float:
    r"""Heating Degree Days

    :param Tn: Minimum day temperature.
    :param Tx: Maximum day temperature.
    :param Tref: Reference temperature.
    """
    if Tref > Tx:
        return Tref - (Tmoy if Tmoy else ((Tn + Tx) / 2))
    elif Tref <= Tn:
        return 0.0
    else:
        return (Tref - Tn) * (0.08 + 0.42 * (Tref - Tn) / (Tx - Tn))

def reqData(
    location: str,
    latitude: float,
    longitude: float,
    start: date,
    today: date,
    delta: timedelta
) -> Point:
    r"""Request data handler
    """
    points = []

    r = requests.get('https://archive-api.open-meteo.com/v1/archive', {
        'latitude': latitude,
        'longitude': longitude,
        'start_date': start - delta,
        'end_date': start,
        'models': 'best_match',
        'daily': [
            'temperature_2m_max',
            'temperature_2m_min',
            'temperature_2m_mean',
        ],
        'timezone': 'Europe/Paris'
    }, timeout=5)
    result = r.json()
    for i in range(len(result['daily']['time'])):
        if not result['daily']['temperature_2m_mean'][i]:
            continue
        points.append(Point('weather')
            .time(datetime.fromisoformat(result['daily']['time'][i]).replace(year=today.year))
            .tag('year', start.year)
            .tag('location', location)
            .field('temperature_min', result['daily']['temperature_2m_min'][i])
            .field('temperature_max', result['daily']['temperature_2m_max'][i])
            .field(
                'temperature_mean',
                result['daily']['temperature_2m_mean'][i]
            )
            .field('degree_day', hdd(
                result['daily']['temperature_2m_min'][i],
                result['daily']['temperature_2m_max'][i],
                result['daily']['temperature_2m_mean'][i],
            )))
    return points


def fetch() -> Point:
    today = date.today() - timedelta(days=1)
    delta = timedelta(days=7)

    points = []

    try:
        for year in range(3):
            points.extend(reqData(
                location='Paris',
                latitude=48.83,
                longitude=2.35,
                start=today.replace(year=today.year - year),
                today=today,
                delta=delta
            ))
        points.extend(reqData(
            location='Copenhagen',
            latitude=55.68,
            longitude=12.57,
            start=today,
            today=today,
            delta=delta
        ))
    except Exception as e:
        capture_exception(e)

    return points

@repeat(every(3).hours)
def weather_exporter():
    points = fetch()
    for point in points:
        influxdb_exporter.InfluxDB().push(point)
