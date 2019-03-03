# -*- coding: utf-8 -*-
# Where to store SQLite database
path_db = '/home/project/ttn_tracker_database.db'

# Where the map initially loads
start_lat = 35.978781
start_lon = -77.855346

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

bing_api_key = ''


def config_app(app, **kwargs):
    """Dash app configuration

    Parameters
    ----------
    app: Dash app
    debug: optional, default=False

    Returns
    -------
    app: Dash app
        With added css, ga and layout container with:
        app-layout: main div, should not be a target of an ouput callback
        page-content: container div, target for an ouput callback
        url: Location, target of an input callback
    """

    if kwargs.get('debug', False):
        app.server.debug = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{db}'.format(db=path_db)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    return app
