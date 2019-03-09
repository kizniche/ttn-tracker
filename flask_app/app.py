import datetime
import logging
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

import os
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from config import app_key
from config import application
from config import bing_api_key
from config import config_app
from config import devices
from config import gateway_locations
from config import path_db
from config import refresh_period_seconds
from config import start_lat
from config import start_lon
from dateutil.parser import parser
from flask import Flask
from flask import jsonify
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

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


@app.route('/dsf673bh')
def main_page():
    get_new_data()
    return render_template('map.html',
                           bing_api_key=bing_api_key,
                           gateway_locations=gateway_locations,
                           location_data=Location.query.all(),
                           refresh_period_seconds=refresh_period_seconds,
                           start_lat=start_lat,
                           start_lon=start_lon)


@app.route('/dsf673bh_past/<seconds>')
def get_past_data(seconds):
    # for testing
    # test_marker = [
    #     {
    #         'device_id': 'test',
    #         'datetime': '2019-02-11T13:51:04.336697974Z',
    #         'date': parser().parse('2019-03-08T16:43:54.720956321Z'),
    #         'latitude': '34.040066',
    #         'longitude': '-84.560319',
    #         'altitude': '200',
    #         'hdop': '3.2'
    #     },
    #     {
    #         'device_id': 'test2',
    #         'datetime': '2019-02-11T13:51:04.336697974Z',
    #         'date': parser().parse('2019-03-08T16:43:54.720956321Z'),
    #         'latitude': '34.045066',
    #         'longitude': '-84.556319',
    #         'altitude': '220',
    #         'hdop': '4'
    #     }
    # ]
    # return jsonify(test_marker)

    # now_utc = datetime.datetime.utcnow()
    #
    # new_location = Location(
    #     device_id='test',
    #     datetime_obj=now_utc,
    #     datetime=now_utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
    #     latitude='34.040066',
    #     longitude='-84.560319',
    #     altitude='300',
    #     hdop='4')
    # db.session.add(new_location)
    # db.session.commit()
    #
    # logger.error("TEST00: save {}".format(now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")))
    #
    # now_utc = datetime.datetime.utcnow()
    #
    # new_location = Location(
    #     device_id='test',
    #     datetime_obj=now_utc,
    #     datetime=now_utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
    #     latitude='34.045066',
    #     longitude='-84.556319',
    #     altitude='300',
    #     hdop='4')
    # db.session.add(new_location)
    # db.session.commit()
    #
    # for each_loc in Location.query.all():
    #     logger.error("TEST01: test {}".format(each_loc.added_at.strftime("%Y-%m-%d %H:%M:%S.%f")))
    #
    # logger.error("TEST01: save {}".format(now_utc.strftime("%Y-%m-%d %H:%M:%S.%f")))

    past_dt_object = datetime.datetime.now() - datetime.timedelta(seconds=int(seconds))

    # logger.error("TEST02: {}".format(past_dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")))

    if seconds_from_last() > 10:
        get_new_data()

    markers = Location.query.filter(Location.added_at > past_dt_object).all()

    # logger.error("TEST03: {} > {}: {}".format(now_utc.strftime("%Y-%m-%d %H:%M:%S.%f"),
    #                                           past_dt_object.strftime("%Y-%m-%d %H:%M:%S.%f"),
    #                                           now_utc > past_dt_object))
    #
    # logger.error("TEST04: {}".format(Location.query.filter(Location.added_at > past_dt_object).count()))

    return jsonify([i.serialize for i in markers])


def get_new_data():
    last_seconds = seconds_from_last()
    if last_seconds:
        past_seconds = int(last_seconds) + 1
    else:
        past_seconds = 604800  # 7 days, max The Things Network storage allows

    for each_device in devices:
        endpoint = "https://{app}.data.thethingsnetwork.org/api/v2/query/{dev}?last={time}".format(
            app=application, dev=each_device, time="{}s".format(past_seconds))
        logger.info(endpoint)
        headers = {"Authorization": app_key}
        response = requests.get(endpoint, headers=headers)
        try:
            for each_resp in response.json():
                if (not Location.query.filter(Location.datetime == each_resp['time']).first() and
                        -90 < float(each_resp['latitude']) <= 90 and -120 <= float(each_resp['longitude']) <= 80):
                    logger.info("{}, {}".format(each_resp['latitude'], each_resp['longitude']))
                    new_location = Location(
                        device_id=each_resp['device_id'],
                        raw=each_resp['raw'],
                        datetime_obj=parser().parse(each_resp['time']),
                        datetime=each_resp['time'],
                        latitude=each_resp['latitude'],
                        longitude=each_resp['longitude'],
                        altitude=each_resp['altitude'],
                        hdop=each_resp['hdop'])
                    db.session.add(new_location)
                    db.session.commit()
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
