## The Things Network Tracker (TTN-Tracker)

For use with [kizniche/ttgo-tbeam-ttnmapper](https://github.com/kizniche/ttgo-tbeam-ttnmapper) for the T-Beam TTGO (tracker node) that transmits data to [The Things Network](https://thethingsnetwork.org) (TTN) for [TTN Mapper](https://ttnmapper.org/).

This Flask app hosts a web-enabled front end using [gunicorn](https://github.com/benoitc/gunicorn) and [nginx](http://nginx.org/). It pulls coordinate data acquired from the tracker node that's been stored on TTN. It stores these coordinates in an SQLite database and displays the coordinates on a map ([leaflet](https://github.com/Leaflet/Leaflet)) in your web browser. This is useful for testing the signal range from gateways while driving, so you can see when and where your signal was able to reach a gateway.

This is very similar to the TTN Mapper frontend, however TTN Mapper takes a long time to update the data points on its map. This software runs locally on your own hardware and responds instantly to new data on TTN, making it a good companion in your vehicle if you want to get instant updates as to whether your tracker node successfully communicated its coordinates or not.

Features include:

 - Multiple map layers, including satellite, topology, and streets (No API keys required)
 - Measuring tool to measure distances between points
 - Map stays focused on the same point across page refreshes (refreshing brings in new data)
 - Clicking gateway or data point markers pops up information about them

### Setup:

I've succesfully set this up on a Raspberry Pi, but these instructions should work for any debian-variant operating system. Other systems you may have to adapt how you install the prerequisites.

```
git clone https://github.com/kizniche/ttn-tracker.git
cd ttn-tracker
sudo pip install virtualenv --upgrade
PYTHON_BINARY_SYS_LOC="$(python3.5 -c "import os; print(os.environ['_'])")"
virtualenv --system-site-packages -p ${PYTHON_BINARY_SYS_LOC} ./env
./env/bin/pip install -r requirements.txt
sudo ln -s /home/pi/ttn-tracker/flask_nginx.conf /etc/nginx/sites-enabled/ttn-tracker_nginx.config
sudo service nginx restart
sudo systemctl enable /home/pi/ttn-tracker/ttn-tracker.service
```

Make sure you have your application set up on The Things Network with the integration "Data Storage". Edit config.py with your application API Key, application ID, Device ID(s), and gateway location(s). The integration "TTN Mapper" is optional but is recommended to be able to provide signal data to the public.

### Run

```sudo service ttn-tracker start```

### Web Address

Note: there is no security preventing someone from viewing this page if they happen to request "/dsf673bh" on the server (however, knowing this is the page is unlikely). Therefore, make sure you are comfortable with this or implement your own security measures such as not allowing port 5500 to be publicly accessible (connect to your home network via VPN to access the app) or add a login system such as [Flask-Login](https://github.com/maxcountryman/flask-login).

http://127.0.0.1:5500/dsf673bh
