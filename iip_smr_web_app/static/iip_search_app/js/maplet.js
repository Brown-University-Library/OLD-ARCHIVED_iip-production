


// maplet_ids.push(maplet_id)

// console.log(maplet_ids);

// var inscrid = window.location.href.slice(-9,-1);
run()


// console.log(inscription_list);

// function run(){
// 	url_xml = "https://library.brown.edu/cds/projects/iip/view_xml/" + inscrid;

// 	var x = new XMLHttpRequest();
// 	x.open("GET", url_xml, true);

// 	x.onreadystatechange = function(){
// 	console.log("onreadystatechange");
// 	if (x.readyState == 4 && x.status == 200){
// 		var doc = x.responseXML;
// 		if(doc.getElementsByTagName("settlement")[0].getAttribute("ref") != null){
// 			var pleiades = doc.getElementsByTagName("settlement")[0].getAttribute("ref");
// 			getCoordinates(pleiades);
// 		}
// 	}
// 	};
// 	x.send(null);
// }


function run(){
	inscription_list.forEach(function(inscrid){
		url_json = "http://library.brown.edu/cds/projects/iip/api/?start=0&rows=100&indent=on&wt=json&q=inscription_id%3A" + inscrid;
		$.getJSON(url_json, function(data){
			if (data["response"]["docs"][0]["city_pleiades"]){
				console.log(inscrid + ": pleiades id detected");
				var pleiades = data["response"]["docs"][0]["city_pleiades"]
				getCoordinates(pleiades, inscrid);
			}
			else{
				console.log(inscrid + ": no pleiades id detected");
					
				drawMaplet(null, inscrid);

				// $("#maplet"+id.toString()).html('<img src="{{STATIC_URL}}iip_search_app/images/placeholder.png" style= "width: 100px; height: 100px;" />');
				console.log(inscrid + ": placed placeholder image");
			}
		});
	});
	
}



function getCoordinates(pleiades, inscrid) {
	if (pleiades.slice(-6) === "380758") {
	    pleiades = "http://pleiades.stoa.org/places/678006";
	}

	$.getJSON('https://pleiades.stoa.org/places/' + pleiades.slice(-6) + '/json', function(data) {
    if (data.reprPoint) {
      drawMaplet(data.reprPoint, inscrid);
    }
    else{
      console.log("error in maplet.js");
    }
  });
}



function drawMaplet(geoCoordinates, inscrid){
	var maplet = L.map("maplet"+inscrid, {zoomControl:false, attributionControl:false}).setView([31.764650, 35.216377], 4)

	var base_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
	        id: 'isawnyu.map-knmctlkh',
	        accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
	    }).addTo(maplet);

	if (geoCoordinates != null){
		L.marker([geoCoordinates[1], geoCoordinates[0]]).addTo(maplet);	
	}	
}




// var myIcon = L.icon({
//     iconUrl: 'marker.png',
//     iconSize: [38, 95],
//     iconAnchor: [22, 94],
//     popupAnchor: [-3, -76],
//     shadowUrl: 'my-icon-shadow.png',
//     shadowSize: [68, 95],
//     shadowAnchor: [22, 94]
// });













