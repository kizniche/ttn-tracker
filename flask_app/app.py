import datetime
import json
import logging
import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from dateutil.parser import parser
from flask import Flask
from flask import jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

from config import app_key
from config import application
from config import bing_api_key
from config import cluster
from config import config_app
from config import devices
from config import gateway_locations
from config import path_db
from config import refresh_period_seconds
from config import start_lat
from config import start_lon

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

app = config_app(Flask(__name__, template_folder="./templates"))
db = SQLAlchemy(app)


def schedule_get_new_data():
    get_new_data()


scheduler = BackgroundScheduler()
job = scheduler.add_job(schedule_get_new_data, 'interval', days=1)
scheduler.start()


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    added_at = db.Column(db.DateTime, default=datetime.datetime.now)
    device_id = db.Column(db.String(250))
    raw = db.Column(db.String(250))
    datetime = db.Column(db.String(250))
    datetime_obj = db.Column(db.DateTime)
    latitude = db.Column(db.String(250))
    longitude = db.Column(db.String(250))
    altitude = db.Column(db.Integer)
    hdop = db.Column(db.Float)

    def __repr__(self):
        return '<ID %r>' % self.id

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'device_id': self.device_id,
            'datetime': self.datetime,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'hdop': self.hdop
        }


class LastAcquisition(db.Model):
    __tablename__ = "last_data"

    id = db.Column(db.Integer, primary_key=True)
    last_datetime = db.Column(db.DateTime)

    def __repr__(self):
        return '<ID %r>' % self.id


if not os.path.exists(path_db):
    db.create_all()


@app.route('/map')
def main_page():
    get_new_data()
    return render_template('map.html',
                           bing_api_key=bing_api_key,
                           devices=devices,
                           gateway_locations=gateway_locations,
                           location_data=Location.query.all(),
                           refresh_period_seconds=refresh_period_seconds,
                           start_lat=start_lat,
                           start_lon=start_lon)


@app.route('/past/<seconds>')
def get_past_data(seconds):
    if seconds_from_last() > 10:
        get_new_data()

    if seconds == '0':
        markers = Location.query.all()
    else:
        past_dt_object = datetime.datetime.now() - datetime.timedelta(seconds=int(seconds))
        markers = Location.query.filter(Location.added_at > past_dt_object).all()
    return jsonify([i.serialize for i in markers])


def get_new_data():
    last_seconds = seconds_from_last()
    if last_seconds:
        past_seconds = int(last_seconds) + 1
    else:
        past_seconds = 604800  # 7 days, max The Things Network storage allows

    for each_device in devices:
        endpoint = "https://{cluster_loc}.cloud.thethings.network/api/v3/as/applications/{app}/devices/{dev}/packages/storage/uplink_message?order=-received_at&type=uplink_message?last={time}".format(
            cluster_loc=cluster, app=application, dev=each_device, time="{}s".format(past_seconds))
        logger.info(endpoint)
        key = 'Bearer {}'.format(app_key)
        headers = {'Accept': 'text/event-stream', 'Authorization': key}
        response = requests.get(endpoint, headers=headers)
        if response.status_code != 200:
            logger.info(response.reason)
        try:
            response_format = "{\"data\": [" + response.text.replace("\n\n", ",")[:-1] + "]}"
            response_data = json.loads(response_format)
            uplink_msg = response_data["data"]
            for each_resp in uplink_msg:
                response_data = each_resp["result"]
                uplink_message = response_data["uplink_message"]

                received = response_data["received_at"]
                lat = uplink_message["decoded_payload"].get("latitude", "")
                lon = uplink_message["decoded_payload"].get("longitude", "")
                alt = uplink_message["decoded_payload"].get("altitude", "")
                qos = uplink_message["decoded_payload"].get("hdop", "")
                end_device_ids = response_data["end_device_ids"]
                device = end_device_ids["device_id"]
                rawpay = uplink_message["frm_payload"]

                if (not Location.query.filter(Location.datetime == received).first() and
                        -90 < float(lat) <= 90 and -120 <= float(lon) <= 80):
                    logger.info("{}, {}".format(lat, lon))
                    new_location = Location(
                        device_id=device,
                        raw=rawpay,
                        datetime_obj=parser().parse(received),
                        datetime=received,
                        latitude=lat,
                        longitude=lon,
                        altitude=alt,
                        hdop=qos)
                    db.session.add(new_location)
                    db.session.commit()
                    logger.info(new_location)
        except:
            pass

    set_date_now()


def set_date_now():
    date_last = LastAcquisition.query.first()
    if not date_last:
        new_last = LastAcquisition(last_datetime=datetime.datetime.now())
        db.session.add(new_last)
        db.session.commit()
    else:
        date_last.last_datetime = datetime.datetime.now()
        db.session.commit()


def seconds_from_last():
    date_last = LastAcquisition.query.first()
    if date_last:
        return (datetime.datetime.now() - date_last.last_datetime).total_seconds()


def distance_coordinates(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance  # km


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
