# -*- coding: utf-8 -*-

# Where the map initially loads
start_lat = 35.978781
start_lon = -77.855346

# Where to store SQLite database
path_db = '/home/pi/ttn-tracker/ttnmapper_retrieve.db'

# TTN Application
application = "ttn_application"
app_key = "key ttn-account-TTN_APP_KEY"

# Application devices
devices = [
    "device_01",
    "device_02"
]

# Where to place gateway markers
gateway_locations = [
    ('Gateway 01', 35.978781, -77.855346),
    ('Gateway 02', 35.978781, -77.655346)
]
