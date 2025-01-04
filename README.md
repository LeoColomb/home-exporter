# Home Exporter

> 🏠 Home InfluxDB Exporter

## About

Rather simple InfluxDB exporter for different data generators at home.

* [GRDF (gaz infra)](src/grdf_exporter/), fetched every half day, for all the available data in the last 7 days;
* [Enedis (electricity infra)](src/enedis_exporter/), fetched every half day, for all the available data in the last 7 days;
* [Weather (min/max temp & degree-day)](src/weather_exporter/), fetched every half day;
* [Air quality (E-AQI & pollens)](src/air_exporter/), fetched every hour;
* [Evohome](src/evohome_exporter/), fetched every minute;
* [InfluxDB (data storage handling)](src/influxdb_exporter/), submitted every 3 seconds if data.

## Usage

Required environment varibles are listed in [`.env.example`](.env.example) file.

### Fly.io

Deployments to Fly.io are configured

### Local

```shell
uv run home-exporter
```

## License

This project is licensed under [MIT License](LICENSE).
