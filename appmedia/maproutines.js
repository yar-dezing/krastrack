// GTS project
// Module contains variable definitions and functions to deal with
// Google map - add markers, draw polyline, draw regions. 
//-----------------------------------------------------------------------------

//<script src="/appmedia/markermanager.js">
//</script>

var arrowIcon = new GIcon();
    arrowIcon.iconSize = new GSize(12,12);
    arrowIcon.shadowSize = new GSize(1,1);
    arrowIcon.iconAnchor = new GPoint(6,6);
    arrowIcon.infoWindowAnchor = new GPoint(6,6);

var baseIcon = new GIcon();
	baseIcon.iconSize=new GSize(12,20);
	baseIcon.iconAnchor=new GPoint(6,20);
	baseIcon.infoWindowAnchor=new GPoint(5,1);

var blueIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_blue.png", null, ""));
var startIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_green.png", null, ""));
var stopIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_red.png", null, ""));
var redIcon = (new GIcon(baseIcon, "http://dig.kraskarta.ru/appmedia/red.png", null, ""));

var customIcons = [];
  	customIcons["blue"] = blueIcon;
  	customIcons["green"] = startIcon;
  	customIcons["red"] = redIcon;

var routePoints = new Array();
var routeMarkers = new Array();
var routeOverlays = new Array();

var loaded_region;

var map = null;
var mgr = null;

var in_ajax = 0;

var lineIx = 0;

var geoXml = new GGeoXml("http://kraskarta.ru/cgi-bin/krsk-city.pl");

//-----------------------------------------------------------------------------
//FUNCTIONS
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
//
funcLoadRegion  = function LoadRegion(data) {
	var route_points = [];
	var xml = GXml.parse(data);
	var routes = xml.documentElement.getElementsByTagName("route");
	
	routePoints[0] = null;
	routeMarkers[0] = null;
	routeOverlays[0] = null;
	//alert(data);
	
	map.clearOverlays();
	
	if (map.getCurrentMapType() != G_NORMAL_MAP) {
		map.addOverlay(geoXml);
	}
	
  	for (var i = 0; i < routes.length; i++) {
		var lat = parseFloat(routes[i].getAttribute("lat"));
    	var lng = parseFloat(routes[i].getAttribute("lng"));
    	route_points[i] = new GLatLng(lat, lng);
    
    }
  
  	loaded_region = new GPolyline(route_points,'#00FF00',3,1);
 	map.addOverlay(loaded_region);
	
	map.setCenter(route_points[0], 8);
	
	in_ajax = 0;
	
	var wait = document.getElementById("wait");
	wait.innerHTML = "";
	
}

//-----------------------------------------------------------------------------
function mapClick(marker, point) {
	var Drawing = document.getElementById("DrawingON");
	if ((Drawing.checked) && (!marker)) {
		addRoutePoint(point);
	}
}

//-----------------------------------------------------------------------------
function gmapShowPPI(ppi) {
	GEvent.trigger(gmapPushPinList[ppi],'click');
}

//-----------------------------------------------------------------------------
//Add new marker on map	
function createMarker(point, info, type) {
	//var marker = new GMarker(point, customIcons[type]);
	var marker = new GMarker(point, type);
    var html = info;
    
    GEvent.addListener(marker, 'click', function() {marker.openInfoWindowHtml(html);});
    
    return marker;
}

//-----------------------------------------------------------------------------
// AJAX. Load XML response from server, which contains Markers data for Devices
funcLoadXML = function LoadXML(data) {
	var points = [];
	var infos = [];
	var icons = [];
	var marker_list = [];
  
  	in_ajax = 0;
  
  	var xml = GXml.parse(data);
  	var markers = xml.documentElement.getElementsByTagName("marker");
	
	//map.clearOverlays();
	
	for (var i = 0; i < markers.length; i++) {
		var lat = parseFloat(markers[i].getAttribute("lat"));
    	var lng = parseFloat(markers[i].getAttribute("lng"));
    	points[i] = new GLatLng(lat, lng);
    
    	infos[i] = markers[i].getAttribute("info");
    	icons[i] = markers[i].getAttribute("icon");
    	//marker_list[i] = createMarker(points[i], info, icon);
  	}
  
 	map.setCenter(points[0], 10);
	
	//map.addOverlay(new GPolyline(points));
	map.addOverlay(new GPolyline(points,'#FF0000',3,1));
	
	midArrows(points, infos, icons);
}

//-----------------------------------------------------------------------------
//DIRECTIONS
//-----------------------------------------------------------------------------
// Returns the bearing in degrees between two points.
// North = 0, East = 90, South = 180, West = 270.

var degreesPerRadian = 180.0 / Math.PI;

function bearing( from, to ) {
	// Convert to radians.
	var lat1 = from.latRadians();
	var lon1 = from.lngRadians();
	var lat2 = to.latRadians();
	var lon2 = to.lngRadians();
	
	// Compute the angle.
	var angle = - Math.atan2( Math.sin( lon1 - lon2 ) * Math.cos( lat2 ), Math.cos( lat1 ) * Math.sin( lat2 ) - Math.sin( lat1 ) * Math.cos( lat2 ) * Math.cos( lon1 - lon2 ) );
	if ( angle < 0.0 )
		angle  += Math.PI * 2.0;

    // And convert result to degrees.
    angle = angle * degreesPerRadian;
    angle = angle.toFixed(1);
	
    return angle;
}

//-----------------------------------------------------------------------------
// A function to put arrow heads at intermediate points
function midArrows(points, infos, icons) {
	if (points.length == 0) {
		return;
	}

	var marker =  createMarker(points[0], infos[0], startIcon);
	map.addOverlay(marker);

	for (var i=1; i < points.length-1; i++) {  
	    var p1=points[i-1];
	    var p2=points[i+1];
	    var dir = bearing(p1,p2);
	    // round it to a multiple of 3 and cast out 120s
	    var dir = Math.round(dir/3) * 3;
	    while (dir >= 120) {dir -= 120;}
	    // use the corresponding triangle marker 
	    arrowIcon.image = "http://www.google.com/intl/en_ALL/mapfiles/dir_"+dir+".png";
	    if (icons[i] == "red") {
	    	var marker =  createMarker(points[i], infos[i], redIcon);
	    	map.addOverlay(marker);
	    	//mgr.addMarker(marker, 8)
	    	}
	    else if (icons[i] == "green") {
	    	var marker =  createMarker(points[i], infos[i], startIcon);
	    	map.addOverlay(marker);
	    	}
	    else {
	    	var marker =  createMarker(points[i], infos[i], arrowIcon);
	    	map.addOverlay(marker);
	    	//mgr.addMarker(marker, 8)
	    	}
    	}
    
    var marker =  createMarker(points[points.length-1], infos[points.length-1], stopIcon);
	map.addOverlay(marker);
}

//-----------------------------------------------------------------------------
//LIMITING REGION
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------    
function addRoutePoint(point) {
	var dist = 0;
	
	if (!routePoints[lineIx]) {
		routePoints[lineIx] = Array();
		routeMarkers[lineIx] = Array();
		routeOverlays[lineIx] = Array();
	}

	routePoints[lineIx].push(point);

	if (routePoints[lineIx].length > 1)	{
		plotRoute();
	}
	else {
		//routeMarkers[lineIx][routePoints[lineIx].length-1] = new GMarker(point,{icon:greenIcon,title:'Start'});
		//map.addOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);
		//map.addOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);

	}
}

//-----------------------------------------------------------------------------
function plotRoute() {
	map.removeOverlay(routeOverlays[lineIx]);
	routeOverlays[lineIx] = new GPolyline(routePoints[lineIx],'#FF0000',3,1);
	map.addOverlay(routeOverlays[lineIx]);

}

//-----------------------------------------------------------------------------
function clearAll() {
	//while (lineIx > 0) {
		resetRoute();
	//}
	
}

//-----------------------------------------------------------------------------
function resetRoute() {
	//if (!routePoints[lineIx] || routePoints[lineIx].length == 0) {
	//	lineIx--;
	//}
	if (routePoints[lineIx]==null) {
		return;
	}
	

	routePoints[lineIx] = null;
	map.removeOverlay(routeOverlays[lineIx]);

	//for (var n = 0 ; n < routeMarkers[lineIx].length ; n++ ) {
	//	var marker = routeMarkers[lineIx][n];
	//	map.removeOverlay(marker);
	//}
	routeMarkers[lineIx] = null;

}

//-----------------------------------------------------------------------------
function undoPoint() {
	if (!routePoints[lineIx] || routePoints[lineIx].length == 0) {
		lineIx--;
	}

	if (routePoints[lineIx].length > 1)	{

		if (routeMarkers[lineIx][routePoints[lineIx].length-1]) {
			var marker = routeMarkers[lineIx].pop();
			map.removeOverlay(marker);
		}
		routePoints[lineIx].pop();
		plotRoute();
	}
	else {
		resetRoute();	
	}
}

//-----------------------------------------------------------------------------
//Build XML file from region markers
function showPoints() {
	var html = '';
	
	html = '<?xml version=\"1.0\" ?>\n';

	html += '<routes>\n';
	var i = 0;

	for (var n = 0 ; n < routePoints[i].length ; n++ ) {
		html += '  <route lat="' + routePoints[i][n].y.toFixed(6) + '" lng="' + routePoints[i][n].x.toFixed(6) + '"';
		html += ' />\n';
	}

	html += '</routes>\n';
	
	return html;
}

//-----------------------------------------------------------------------------
function addClosing() {
	if (routePoints[lineIx].length > 1)	{
		lineIx++;

	}
}
