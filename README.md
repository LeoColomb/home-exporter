# Home Exporter

> 🏠 Home InfluxDB Exporter

## About

Rather simple InfluxDB exporter for different data generators at home.

* [GRDF (gaz provider)](grdf_exporter/), fetched every half day, for all the available data in the last 15 days;
* [Siemens LOGO! (Siemens PLC via S7)](logo_exporter/), fetched every second;
* [Weather (min/max temp & degree-day)](temp_exporter), fetched every half day;
* [InfluxDB (data storage handling)](influxdb_exporter/), submitted every 3 seconds.

## Usage

To be documented.
So far, deployments to Fly.io are configured, and required environment varibles are listed in [`example.env`](example.env) file.

## License

This project is licensed under [MIT License](LICENSE).
