## The Things Network Tracker (TTN-Tracker)

This is a [Flask](http://flask.pocoo.org/) app served via [Gunicorn](https://github.com/benoitc/gunicorn) and [Nginx](http://nginx.org/) using [docker](https://www.docker.com/) containers orchestrated by docker-compose.

For use with [kizniche/ttgo-tbeam-ttnmapper](https://github.com/kizniche/ttgo-tbeam-ttnmapper) for the T-Beam TTGO (tracker node) that transmits data to [The Things Network](https://thethingsnetwork.org) (TTN) for [TTN Mapper](https://ttnmapper.org/).

This app pulls coordinate data acquired from the tracker node that's been stored on TTN. It stores these coordinates in an SQLite database and displays the coordinates on a map ([leaflet](https://github.com/Leaflet/Leaflet)) in your web browser. This is useful for testing the signal range from gateways while driving, so you can see when and where your signal was able to reach a gateway.

This is very similar to the TTN Mapper frontend, however TTN Mapper takes a long time to update the data points on its map. This software runs locally on your own hardware and responds instantly to new data on TTN, making it a good companion in your vehicle if you want to get instant updates as to whether your tracker node successfully communicated its coordinates or not.

Features include:

 - Multiple map layers, including satellite, topology, and streets (No API keys required)
 - Measuring tool to measure distances between points
 - Map stays focused on the same point across page refreshes (refreshing brings in new data)
 - Clicking gateway or data point markers pops up information about them

### Setup:

I've successfully set this up on a Raspberry Pi.

Make sure you have your application set up on The Things Network with the integration "Data Storage". The integration "TTN Mapper" is optional but is recommended to be able to provide signal data to the public.

### Install docker and docker-compose

```
curl -sSL https://get.docker.com | sh
sudo pip install docker-compose
```

### Clone this repository

```
git clone https://github.com/kizniche/ttn-tracker.git
cd ttn-tracker
```

### Edit the config file

Edit ttn-tracker/flask_app/config.py with your application API Key, application ID, Device ID(s), and gateway location(s) before building the docker image. If you need to edit this file after the image is created, you can rebuild the image (destroying data) or copy the new config file over the old while the flask_app container is running (see below).

### Build and start the app

This will build and start the app and keep it running across reboots.

```sudo make build```

### Stop app (preserving data)

```sudo docker-compose stop```

### Start app after stopping

```sudo docker-compose start```

### Web Address

Open a browser to this address, replacing IP_ADDRESS with the IP address of the system running the docker containers.

http://IP_ADDRESS:5550/dsf673bh

Note: there is no security preventing someone from viewing this page if they happen to request "/dsf673bh" on the server (however, knowing this is the page is unlikely). Therefore, make sure you are comfortable with this or implement your own security measures such as not allowing port 5550 to be publicly accessible (connect to your home network via VPN to access the app) or add a login system such as [Flask-Login](https://github.com/maxcountryman/flask-login).

### Notes

#### Stop app and delete data (keep containers)

```sudo docker-compose down```

#### Stop app and delete containers

```sudo docker-compose rm -fs```

#### List docker containers

```sudo docker ps```

#### Start a shell in a docker container

```sudo docker exec -i -t CONTAINER_ID /bin/bash```

#### Copy files to/from a docker container

```
docker cp foo.txt CONTAINER_ID:/foo.txt
docker cp CONTAINER_ID:/foo.txt foo.txt
```
