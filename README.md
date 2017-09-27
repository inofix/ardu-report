# ardu-report

[![Travis CI](https://img.shields.io/travis/zwischenloesung/ardu-report.svg?style=flat)](http://travis-ci.org/zwischenloesung/ardu-report)

Python library and CLI to report back the sensor data from our arduino(s).

## Basic Idea

For now we have one arduino reporting sensor values back over the serial line.
On the other end there is a raspberry pi collecting the data. The data is then processed and either just printed to the console or a file, or sent over mobile or wired/wireless network to, e.g., a webserver..

If more than one arduino are connected. For each one of them the data processing can be configured individually.

## Example Data for Python Processing

### INPUT: JSON from the arduino over the serial line

  [
    {"id":"light_value","value":"777"},
    {"id":"box_temperature","unit":"°C","value":"22.19"},
    {"id":"env_temperature","unit":"°C","value":"20.00"},
    {"id":"env_humidity","unit":"%","value":"71.00"},
    {"id":"env_heat_index","value":"19.91"},
    {"id":"water_level","threshold":"600","value":"0"},
    {"id":"water_distance","unit":"m","value":"0.92"}
  ]

### OUTPUT: Target JSON from the raspberry pi for the use in web app

  [
    {"id":"light_value","value":"777", "time"="2017-09-20T21:29:42"},
    {"id":"light_value","value":"777", "time"="2017-09-20T21:39:51"},
    {"id":"light_value","value":"777", "time"="2017-09-20T21:49:49"},
    {"id":"box_temperature","unit":"°C","value":"22.19", "time"="2017-09-20T21:49:49"},
    {"id":"env_temperature","unit":"°C","value":"20.00", "time"="2017-09-20T21:49:49"},
    {"id":"env_humidity","unit":"%","value":"71.00", "time"="2017-09-20T21:49:49"},
    {"id":"env_heat_index","value":"19.91", "time"="2017-09-20T21:49:49"},
    {"id":"water_level","threshold":"600","value":"0", "time"="2017-09-20T21:49:49"},
    {"id":"water_distance","unit":"m","value":"0.92", "time"="2017-09-20T21:49:49"}
  ]

