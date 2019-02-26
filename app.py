import datetime
import logging
from math import atan2
from math import cos
from math import radians
from math import sin
from math import sqrt

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

from config import app_key
from config import application
from config import devices
from config import gateway_locations
from config import path_db
from config import start_lat
from config import start_lon

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="./templates")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{db}'.format(db=path_db)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def schedule_get_new_data():
    get_new_data()


scheduler = BackgroundScheduler()
job = scheduler.add_job(schedule_get_new_data, 'interval', days=1)
scheduler.start()


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(250))
    last_data_date = db.Column(db.DateTime)
    raw = db.Column(db.String(250))
    datetime = db.Column(db.String(250))
    latitude = db.Column(db.String(250))
    longitude = db.Column(db.String(250))
    altitude = db.Column(db.Integer)
    hdop = db.Column(db.Float)

    def __repr__(self):
        return '<ID %r>' % self.id


class LastAcquisition(db.Model):
    __tablename__ = "last_data"

    id = db.Column(db.Integer, primary_key=True)
    last_datetime = db.Column(db.DateTime)

    def __repr__(self):
        return '<ID %r>' % self.id


@app.route('/dsf673bh')
def hello_world():
    get_new_data()
    return render_template('map.html',
                           gateway_locations=gateway_locations,
                           location_data=Location.query.all(),
                           start_lat=start_lat,
                           start_lon=start_lon)


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
    app.run(debug=True, host='0.0.0.0', port=5500)
