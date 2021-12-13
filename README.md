## The Things Network Tracker (TTN-Tracker)

This is a [Flask](http://flask.pocoo.org/) app served via [Gunicorn](https://github.com/benoitc/gunicorn) and [Nginx](http://nginx.org/) using [docker](https://www.docker.com/) containers orchestrated by docker-compose.

For use with TTN Mapper nodes such as [kizniche/ttgo-tbeam-ttnmapper](https://github.com/kizniche/ttgo-tbeam-ttnmapper) for the T-Beam TTGO (tracker node), which transmits data to [The Things Network](https://thethingsnetwork.org) (TTN) for [TTN Mapper](https://ttnmapper.org/).

This app pulls coordinate data acquired from the tracker node that's been stored on TTN. It stores these coordinates in an SQLite database and displays the coordinates on a [leaflet](https://github.com/Leaflet/Leaflet) map in your web browser. This is useful for testing the signal range from LoRaWAN gateways while driving, so you can see when and where your signal was able to reach a gateway.

This is very similar to the TTN Mapper frontend, however TTN Mapper takes a long time to update the data points on its map. This software runs locally on your own hardware and responds instantly to new data on TTN when the browser page is refreshed, making it a good companion in your vehicle if you want to get instant updates as to whether your tracker node successfully transmitted its coordinates or not.

![TTN Tracker 01](https://raw.githubusercontent.com/kizniche/ttn-tracker/master/images/Screenshot_TTN_Tracker_01.png)

Web browser view of TTN Tracker with the gateway (blue marker) and points where the tracking node successfully transmitted to the gateway (red marks).

### Platforms

Successfully built this on the Raspberry Pi (Raspbian Buster) and a desktop PC (64-bit Ubuntu 18.04.2). However, since this is docker, it should run on a variety of other platforms.

### Features

 - Multiple map layers, including topology, streets, and satellite ([Bing API key](https://www.bingmapsportal.com) required for satellite)
 - Automatically acquires new data and adds markers to the map
 - Tracking tool to use device GPS to place marker of current position (and direction) on map
 - Scale bar at edge of map
 - SSL/HTTPS (required for location tracking)
 - Measuring tool for measure distances between points
 - Map stays focused on the same point across page refreshes
 - Clicking gateway or data point markers pops up information about them
 - Toggle visibility of markers of each device on map
 - Select age of markers to show on map

### TODO

 - Add user-configurable auto-refresh


## Install

Make sure you have your application set up on The Things Network with the integration "Data Storage". The integration "TTN Mapper" is optional but is recommended to be able to provide signal data to the public.


### Install dependencies

```
sudo apt-get install -y libffi-dev libssl-dev
```

### Install docker and docker-compose

```
curl -sSL https://get.docker.com | sh
sudo apt-get install -y python3 python3-pip
sudo pip3 install docker-compose
```

### Add user to docker group

```
sudo usermod -a -G docker $USER
```

Then log out and back in again.

### Clone this repository

```
git clone https://github.com/kizniche/ttn-tracker.git
cd ttn-tracker
```

### Edit the config file

Edit `ttn-tracker/flask_app/config.py` with your application API Key, application ID, Device ID(s), gateway location(s), and Bing map API key (optional) before building the docker images. If you need to edit this file after the images are created, you can rebuild the image (destroying data) or copy the new config file over the old file while the flask_app container is running (see [Notes](#notes), below).

```
nano flask_app/config.py
```

### Build and start the services

```
make build
```

### Access the app

Open a web browser to the address, below, replacing IP_ADDRESS with the IP address of the system running the docker containers.

```https://IP_ADDRESS/map```

Note: there is no security preventing someone from viewing this page if they happen to request "/map" on the server (however, knowing this is the page is unlikely). Therefore, make sure you are comfortable with this or implement your own security measures such as not allowing port 443 to be publicly accessible (connect to your home network via VPN to access the app) or add a login system such as [Flask-Login](https://github.com/maxcountryman/flask-login).


## Notes

### Stop services (preserving data)

```
docker-compose stop
```

### Start services

```
docker-compose start
```

### Stop services and delete data (keep containers)

```
docker-compose down
```

### Stop services and delete containers

```
docker-compose rm -fs
```

### List docker containers

```
docker ps
```

### View container log

```
docker logs flask_app
```

### Start a shell in a docker container

```
docker exec -i -t CONTAINER_ID /bin/bash
```

### Copy a file to a docker container

```
docker cp ./foo.txt CONTAINER_ID:/foo.txt
```

### Copy a file from a docker container

```
docker cp CONTAINER_ID:/foo.txt ./foo.txt
```
