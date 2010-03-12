// GTS project
// Module contains variable definitions and functions to deal with
// Google map - add markers, draw polyline, draw regions. 
//-----------------------------------------------------------------------------

var iconBlue = new GIcon(); 
  	iconBlue.image = 'http://labs.google.com/ridefinder/images/mm_20_blue.png';
  	iconBlue.shadow = 'http://labs.google.com/ridefinder/images/mm_20_shadow.png';
  	iconBlue.iconSize = new GSize(12, 20);
  	iconBlue.shadowSize = new GSize(22, 20);
  	iconBlue.iconAnchor = new GPoint(6, 20);
  	iconBlue.infoWindowAnchor = new GPoint(5, 1);

var iconGreen = new GIcon(); 
  	iconGreen.image = 'http://labs.google.com/ridefinder/images/mm_20_green.png';
  	iconGreen.shadow = 'http://labs.google.com/ridefinder/images/mm_20_shadow.png';
  	iconGreen.iconSize = new GSize(12, 20);
  	iconGreen.shadowSize = new GSize(22, 20);
  	iconGreen.iconAnchor = new GPoint(6, 20);
  	iconGreen.infoWindowAnchor = new GPoint(5, 1);

var iconRed = new GIcon(); 
  	iconRed.image = 'http://labs.google.com/ridefinder/images/mm_20_red.png';
  	iconRed.shadow = 'http://labs.google.com/ridefinder/images/mm_20_shadow.png';
  	iconRed.iconSize = new GSize(12, 20);
  	iconRed.shadowSize = new GSize(22, 20);
  	iconRed.iconAnchor = new GPoint(6, 20);
  	iconRed.infoWindowAnchor = new GPoint(5, 1);

var customIcons = [];
  	customIcons["blue"] = iconBlue;
  	customIcons["green"] = iconGreen;
  	customIcons["red"] = iconRed;

var baseIcon = new GIcon();
	baseIcon.iconSize=new GSize(12,20);
	baseIcon.iconAnchor=new GPoint(6,10);
	baseIcon.infoWindowAnchor=new GPoint(5,1);

var greenIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_green.png", null, ""));
var redIcon = (new GIcon(baseIcon, "http://labs.google.com/ridefinder/images/mm_20_red.png", null, ""));

var routePoints = new Array();
var routeMarkers = new Array();
var routeOverlays = new Array();

var map;
var lineIx = 0;

//-----------------------------------------------------------------------------
//Add new marker on map	
function createMarker(point, info, type) {
	var marker = new GMarker(point, customIcons[type]);
    var html = info;
    
    GEvent.addListener(marker, 'click', function() {marker.openInfoWindowHtml(html);});
    
    return marker;
}

//-----------------------------------------------------------------------------
function mapClick(marker, point) {
	if (!marker) {
		addRoutePoint(point);
	}
}

//-----------------------------------------------------------------------------    
function addRoutePoint(point) {
	var dist = 0;

	if (!routePoints[lineIx]) {
		routePoints[lineIx] = Array();
		routeMarkers[lineIx] = Array();
	}

	routePoints[lineIx].push(point);

	if (routePoints[lineIx].length > 1)	{
		plotRoute();
	}
	else {
		routeMarkers[lineIx][routePoints[lineIx].length-1] = new GMarker(point,{icon:greenIcon,title:'Start'});
		map.addOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);

	}
}

//-----------------------------------------------------------------------------
//function getMapcenter() {
//	var center = map.getCenter();
//	var z = map.getZoom();
//}

//-----------------------------------------------------------------------------    
//function DEC2DMS(dec) {
//
//	var deg = Math.floor(Math.abs(dec));
//	var min = Math.floor((Math.abs(dec)-deg)*60);
//	var sec = (Math.round((((Math.abs(dec) - deg) - (min/60)) * 60 * 60) * 100) / 100 ) ;
//
//	deg = dec < 0 ? deg * -1 : deg;
//
//	var dms  = deg + '&deg ' + min + '\' ' + sec + '"';
//	return dms;
//}

//-----------------------------------------------------------------------------
function plotRoute() {
	map.removeOverlay(routeOverlays[lineIx]);
	routeOverlays[lineIx] = new GPolyline(routePoints[lineIx],'#FF0000',3,1);
	map.addOverlay(routeOverlays[lineIx]);

}

//-----------------------------------------------------------------------------
function clearAll() {
	while (lineIx > 0) {
		resetRoute();
	}
	
}

//-----------------------------------------------------------------------------
function resetRoute() {
	if (!routePoints[lineIx] || routePoints[lineIx].length == 0) {
		lineIx--;
	}

	routePoints[lineIx] = null;
	map.removeOverlay(routeOverlays[lineIx]);

	for (var n = 0 ; n < routeMarkers[lineIx].length ; n++ ) {
		var marker = routeMarkers[lineIx][n];
		map.removeOverlay(marker);
	}
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
function showPoints(xml) {
	var html = '';
	if (xml) {
		html = '<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n';

		html += '<routes>\n';
		for (var i = 0 ; i < lineIx ; i++ ) {
			html += '  <route>\n';
			for (var n = 0 ; n < routePoints[i].length ; n++ ) {
				html += '    <p lat="' + routePoints[i][n].y.toFixed(8) + '" lon="' + routePoints[i][n].x.toFixed(8) + '"';
				if (routeMarkers[i][n]) {
					html += ' markerIcon="'+ routeMarkers[i][n].getIcon().image +'"';
				}
				html += ' />\n';
			}

			html += '  </route>\n';
		}
		html += '</routes>\n';
	}
	else {
		for (var i = 0 ; i < lineIx ; i++ ) {
			for (var n = 0 ; n < routePoints[i].length ; n++ ) {
				html += routePoints[i][n].y.toFixed(8) + ', ' + routePoints[i][n].x.toFixed(8) + '\n';
			}
			html += '----- new line ------ \n';
		}
	}

	if (html == '') {
		html += 'You must add a closing point to each line\n\n';
	}

	html += '\n\n';
//	html += encodePolyline();

	var nWin = window.open('','nWin','width=780,height=500,left=50,top=50,resizable=1,scrollbars=yes,menubar=no,status=no');
	nWin.focus();
	nWin.document.open ('text/xml\n\n');
	nWin.document.write(html);
	nWin.document.close();
}

//-----------------------------------------------------------------------------
//function addIntermediate() {
//	if (routePoints[lineIx].length > 1)	{
//		map.removeOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);
//		routeMarkers[lineIx][routePoints[lineIx].length-1] = new GMarker(routePoints[lineIx][routePoints[lineIx].length-1],{icon:yellowIcon,title:'Point '+ routePoints[lineIx].length-1});
//		map.addOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);
//	}
//}

//-----------------------------------------------------------------------------
function addClosing() {
	if (routePoints[lineIx].length > 1)	{
		map.removeOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);
		routeMarkers[lineIx][routePoints[lineIx].length-1] = new GMarker(routePoints[lineIx][routePoints[lineIx].length-1],{icon:redIcon,title:'End'});
		map.addOverlay(routeMarkers[lineIx][routePoints[lineIx].length-1]);
		lineIx++;

	}
}

//-----------------------------------------------------------------------------
function encodePolyline() {
	var encodedPoints = '';
	var	encodedLevels = '';

	var plat = 0;
	var plng = 0;

	for (var n = 0 ; n < routePoints[lineIx].length ; n++ ) {
		var lat = routePoints[lineIx][n].y.toFixed(8);
		var lng = routePoints[lineIx][n].x.toFixed(8);

		var level = (n == 0 || n == routePoints[lineIx].length-1) ? 3 : 1;
		var level = 0;

		var late5 = Math.floor(lat * 1e5);
		var lnge5 = Math.floor(lng * 1e5);

		dlat = late5 - plat;
		dlng = lnge5 - plng;

		plat = late5;
		plng = lnge5;

		encodedPoints += encodeSignedNumber(dlat) + encodeSignedNumber(dlng);
		encodedLevels += encodeNumber(level);
	}


	var html = '';
	html += 'new GPolyline.fromEncoded({\n';
	html += '  color: "#0000ff",\n';
	html += '  weight: 4,\n';
	html += '  opacity: 0.8,\n';
	html += '  points: "'+encodedPoints+'",\n';
	html += '  levels: "'+encodedLevels+'",\n';
	html += '  zoomFactor: 16,\n';
	html += '  numLevels: 4\n';
	html += '});\n';

	return html;
}

//-----------------------------------------------------------------------------
function encodeSignedNumber(num) {
	var sgn_num = num << 1;

	if (num < 0) {
		sgn_num = ~(sgn_num);
	}

	return(encodeNumber(sgn_num));
}

//-----------------------------------------------------------------------------
// Encode an unsigned number in the encode format.
function encodeNumber(num) {
	var encodeString = "";

	while (num >= 0x20) {
		encodeString += (String.fromCharCode((0x20 | (num & 0x1f)) + 63));
		num >>= 5;
	}

	encodeString += (String.fromCharCode(num + 63));
	return encodeString;
}
