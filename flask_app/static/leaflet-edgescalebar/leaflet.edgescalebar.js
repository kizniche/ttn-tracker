/*
 *  Draws the metric scale bars in Web Mercator map along top and right edges. 
 *  Authors: Dražen Tutić (dtutic@geof.hr), Ana Kuveždić Divjak (akuvezdic@geof.hr)
 *  	     University of Zagreb, Faculty of Geodesy, GEOF-OSGL Lab
 *  Inspired by LatLonGraticule Leaflet plugin by: lanwei@cloudybay.com.tw
 */

L.EdgeScaleBar = L.Layer.extend({
    includes: L.Mixin.Events,

    options: {
        opacity: 1,
        weight: 0.8,
        color: '#000',
        font: '11px Arial',
        zoomInterval: [
            {start: 1, end: 2, interval: 5000000},
            {start: 3, end: 3, interval: 2000000},
            {start: 4, end: 4, interval: 1000000},
            {start: 5, end: 5, interval: 500000},
            {start: 6, end: 7, interval: 200000},
            {start: 8, end: 8, interval: 100000},
            {start: 9, end: 9, interval: 50000},
            {start: 10, end: 10, interval: 20000},
            {start: 11, end: 11, interval: 10000},
            {start: 12, end: 12, interval: 5000},
            {start: 13, end: 13, interval: 2000},
            {start: 14, end: 14, interval: 1000},
            {start: 15, end: 15, interval: 500},
            {start: 16, end: 16, interval: 200},
            {start: 17, end: 17, interval: 100},
            {start: 18, end: 18, interval: 50},
            {start: 19, end: 19, interval: 20},
            {start: 20, end: 20, interval: 10}
        ]
    },

    initialize: function (options) {

        L.setOptions(this, options);

	//Constants of the WGS84 ellipsoid needed to calculate meridian length or latitute
        this._a = 6378137.0;
	this._b = 6356752.3142;
	this._e2 = (this._a*this._a - this._b*this._b)/(this._a*this._a);
	this._n = (this._a - this._b)/(this._a + this._b);
	this._n2 = this._n * this._n;
	this._A = this._a*(1.0 - this._n)*(1.0 - this._n2)*(1.0 + 9.0/4.0*this._n2 + 225.0/64.0*this._n2*this._n2);
	this._ic1 = 1.5*this._n - 29.0/12.0*this._n2*this._n + 553.0/80.0*this._n2*this._n2*this._n;
	this._ic2 = 21.0/8.0*this._n2 - 1537.0/128.0*this._n2*this._n2;
	this._ic3 = 151.0/24.0*this._n2*this._n - 32373.0/640.0*this._n2*this._n2*this._n;
	this._ic4 = 1097.0/64.0*this._n2*this._n2;
	this._ic5 = 8011.0/150.0*this._n2*this._n2*this._n;
	this._c1 = -1.5*this._n + 31.0/24.0*this._n2*this._n - 669.0/640.0*this._n2*this._n2*this._n;
	this._c2 = 15.0/18.0*this._n2 - 435.0/128.0*this._n2*this._n2;
	this._c3 = -35.0/12.0*this._n2*this._n + 651.0/80.0*this._n2*this._n2*this._n;
	this._c4 = 315.0/64.0*this._n2*this._n2;
	this._c5 = -693.0/80.0*this._n2*this._n2*this._n;

	//Latitude limit of the Web Mercator projection
	this._LIMIT_PHI = 1.484419982;
    },

    onAdd: function (map) {
        this._map = map;

        if (!this._container) {
            this._initCanvas();
        }

        map._panes.overlayPane.appendChild(this._container);

        map.on('viewreset', this._reset, this);
        map.on('move', this._reset, this);
        map.on('moveend', this._reset, this);

        this._reset();
    },

    onRemove: function (map) {
        map.getPanes().overlayPane.removeChild(this._container);

        map.off('viewreset', this._reset, this);
        map.off('move', this._reset, this);
        map.off('moveend', this._reset, this);
    },

    addTo: function (map) {
        map.addLayer(this);
        return this;
    },

    setOpacity: function (opacity) {
        this.options.opacity = opacity;
        this._updateOpacity();
        return this;
    },

    bringToFront: function () {
        if (this._canvas) {
            this._map._panes.overlayPane.appendChild(this._canvas);
        }
        return this;
    },

    bringToBack: function () {
        var pane = this._map._panes.overlayPane;
        if (this._canvas) {
            pane.insertBefore(this._canvas, pane.firstChild);
        }
        return this;
    },

    getAttribution: function () {
        return this.options.attribution;
    },

    _initCanvas: function () {
        this._container = L.DomUtil.create('div', 'leaflet-image-layer');

        this._canvas = L.DomUtil.create('canvas', '');
        this._ctx = this._canvas.getContext('2d');

	this._vert_gradientFill=this._ctx.createLinearGradient(0,0,0,10);
	this._vert_gradientFill.addColorStop(0,"rgba(255, 255, 255, 1)");
	this._vert_gradientFill.addColorStop(1,"rgba(255, 255, 255, 0)");

	this._hor_gradientFill=this._ctx.createLinearGradient(this._map.getSize().x-10,0,this._map.getSize().x,0);
	this._hor_gradientFill.addColorStop(0,"rgba(255, 255, 255, 0)");
	this._hor_gradientFill.addColorStop(1,"rgba(255, 255, 255, 1)");

        this._updateOpacity();

        this._container.appendChild(this._canvas);

        L.extend(this._canvas, {
            onselectstart: L.Util.falseFn,
            onmousemove: L.Util.falseFn,
            onload: L.bind(this._onCanvasLoad, this)
        });
    },

    _reset: function () {
        var container = this._container,
            canvas = this._canvas,
            size = this._map.getSize(),
            lt = this._map.containerPointToLayerPoint([0, 0]);

        L.DomUtil.setPosition(container, lt);

        container.style.width = size.x + 'px';
        container.style.height = size.y + 'px';

        canvas.width  = size.x;
        canvas.height = size.y;
        canvas.style.width  = size.x + 'px';
        canvas.style.height = size.y + 'px';

	this._ctx.fillStyle= this._vert_gradientFill;
	this._ctx.fillRect(0,0,size.x,10);
	this._ctx.fillStyle= this._hor_gradientFill;
	this._ctx.fillRect(size.x-10,0,size.x,size.y);

	this._ctx.beginPath();
        this._ctx.moveTo(0,0);
        this._ctx.lineTo(size.x,0);
        this._ctx.lineTo(size.x,size.y);
        this._ctx.stroke();

        this._calcInterval();
	this._draw();	
    },

    _onCanvasLoad: function () {
        this.fire('load');
    },

    _updateOpacity: function () {
        L.DomUtil.setOpacity(this._canvas, this.options.opacity);
    },

    _calcInterval: function() {
        var zoom = this._map.getZoom();
        for (var idx in this.options.zoomInterval) {
            var dict = this.options.zoomInterval[idx];
            if (dict.start <= zoom) {
                if (dict.end && dict.end >= zoom) {
                    this._dd = dict.interval;
                    break;
                }
            }
        }
        this._currZoom = zoom;
    },

    _draw: function() {
        this._ctx.strokeStyle = this.options.color;    
	this._create_lat_ticks();
	this._create_lon_ticks();

        this._ctx.fillStyle = this.options.color;
        this._ctx.font = this.options.font;
	var units = ' m', dd = this._dd;
	if (this._dd >= 1000) { units = ' km'; dd = this._dd/1000; }
	this._ctx.textAlign="right";
	this._ctx.textBaseline="middle"; 
        this._ctx.fillText(dd + units, this._map.getSize().x-12, this._map.getSize().y/2);
	this._ctx.textAlign="center";
	this._ctx.textBaseline="top"; 
        this._ctx.fillText(dd + units, this._map.getSize().x/2, 12);
    },

    _create_lat_ticks: function() {
	var phi_s = this._map.containerPointToLatLng(L.point(0,this._map.getSize().y/2)).lat;
	var phi_d = this._map.containerPointToLatLng(L.point(0,this._map.getSize().y)).lat;
	var phi_g = this._map.containerPointToLatLng(L.point(0,0)).lat;
	var d_s = this._merLength(phi_s*Math.PI/180.0);
	var d_g = this._merLength(phi_g*Math.PI/180.0);
	var d_d = this._merLength(phi_d*Math.PI/180.0);
	    
	// draw major ticks    
	for (i = d_s+this._dd/2; i < d_g; i = i + this._dd) {
	    var phi = this._invmerLength(i);			
	    if ((phi < this._LIMIT_PHI) && (phi > -this._LIMIT_PHI)) this._draw_lat_tick(phi,10,this.options.weight*1.5);
	}
	for (i = d_s-this._dd/2; i > d_d; i = i - this._dd) {
	    var phi = this._invmerLength(i);			
	    if ((phi > -this._LIMIT_PHI) && (phi < this._LIMIT_PHI)) this._draw_lat_tick(phi,10,this.options.weight*1.5);
	}
	    
	// draw minor ticks    
	for (i = d_s; i < d_g; i = i + this._dd/10.0) {
	    var phi = this._invmerLength(i);			
	    if ((phi < this._LIMIT_PHI) && (phi > -this._LIMIT_PHI)) this._draw_lat_tick(phi,4,this.options.weight);
	}
	for (i = d_s-this._dd/10; i > d_d; i = i - this._dd/10) {
	    var phi = this._invmerLength(i);			
	    if ((phi > -this._LIMIT_PHI) && (phi < this._LIMIT_PHI)) this._draw_lat_tick(phi,4,this.options.weight);
	}
    },

    _create_lon_ticks: function() {
	var cen_p = this._map.containerPointToLatLng(L.point(this._map.getSize().x/2,0));
	var left_p = this._map.containerPointToLatLng(L.point(0,0));
	var right_p = this._map.containerPointToLatLng(L.point(this._map.getSize().x,0));
	var sinPhi = Math.sin(cen_p.lat*Math.PI/180.0);
	var N = this._a/Math.sqrt(1.0-this._e2*sinPhi*sinPhi);
	var dl = this._dd/(N*Math.cos(cen_p.lat*Math.PI/180.0))*180.0/Math.PI;
	    
	// draw major ticks    
	for (i = cen_p.lng+dl/2; i < right_p.lng; i = i + dl) this._draw_lon_tick(i,10,this.options.weight*1.5);
	for (i = cen_p.lng-dl/2; i > left_p.lng; i = i - dl) this._draw_lon_tick(i,10,this.options.weight*1.5);
	
	// draw minor ticks    
	for (i = cen_p.lng; i < right_p.lng; i = i + dl/10) this._draw_lon_tick(i,4,this.options.weight);
	for (i = cen_p.lng-dl/10; i > left_p.lng; i = i - dl/10) this._draw_lon_tick(i,4,this.options.weight);
    },

    _latLngToCanvasPoint: function (latlng) {
        var projectedPoint = this._map.project(L.latLng(latlng));
        projectedPoint._subtract(this._map.getPixelOrigin());
        return L.point(projectedPoint).add(this._map._getMapPanePos());
    },

    _draw_lat_tick: function (phi, size, weight) {
	var y = this._latLngToCanvasPoint(L.latLng(phi*180.0/Math.PI, 0.0)).y;
	this._ctx.lineWidth = weight;
	this._ctx.beginPath();
        this._ctx.moveTo(this._map.getSize().x, y);
        this._ctx.lineTo(this._map.getSize().x-size, y);
        this._ctx.stroke();
    },

    _draw_lon_tick: function(lam, size, weight) {
	var x = this._latLngToCanvasPoint(L.latLng(0.0, lam)).x;
	this._ctx.lineWidth = weight;
	this._ctx.beginPath();
        this._ctx.moveTo(x, 0);
        this._ctx.lineTo(x, size);
        this._ctx.stroke();
    },

    _merLength: function(phi) {
	var cos2phi = Math.cos(2.0*phi);
	return this._A*(phi+Math.sin(2.0*phi)*(this._c1+(this._c2+(this._c3+(this._c4+this._c5*cos2phi)*cos2phi)*cos2phi)*cos2phi));
    },

    _invmerLength: function(s) {
	var psi = s/this._A;
	var cos2psi = Math.cos(2.0*psi);
	return psi+Math.sin(2.0*psi)*(this._ic1+(this._ic2+(this._ic3+(this._ic4+this._ic5*cos2psi)*cos2psi)*cos2psi)*cos2psi);
    }
});

L.edgeScaleBar = function (options) {
    return new L.EdgeScaleBar(options);
};
