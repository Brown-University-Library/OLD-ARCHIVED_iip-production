// GLOBAL VARS

// base url for getting all inscriptions
// var BASE_URL = 'https://library.brown.edu/cds/projects/iip/api/?start=0&rows=3278&indent=on&fl=inscription_id,region,city,city_geo,notBefore,notAfter,placeMenu,type,physical_type,language,language_display,religion,material&wt=json&group=true&group.field=city_pleiades&group.limit=-1&q=*:*';
var BASE_URL = 'https://library.brown.edu/cds/projects/iip/api/?start=0&rows=6000&indent=on&fl=inscription_id,region,city,city_geo,notBefore,notAfter,placeMenu,type,physical_type,language,language_display,religion,material&wt=json&group=true&group.field=city_pleiades&group.limit=-1&q=*:*';
// url for applying filters to base url
var FILTERS_URL = BASE_URL.concat("&fq=");
//url for getting all pleiades urls from database
var LOCATIONS_URL = 'https://library.brown.edu/cds/projects/iip/api/?q=*:*&%3A*&start=0&rows=0&indent=on&facet=on&facet.field=city_pleiades&wt=json';
// layer of points for inscriptions on map
var points_layer = L.layerGroup();
// map of each type of filters and the specific filter names that are being applied (e.g. place: ['Coastal Plain', 'Golan'])
var filters = {
  place: [],
  type: [],
  physical_type: [],
  language: [],
  religion: [],
  material: []
};
// map of concatenators for multiple filters. default is 'OR' unless set to AND
var ops = {
  place: ' OR ',
  type: ' OR ',
  physical_type: ' OR ',
  language: ' OR ',
  religion: ' OR ',
  material: ' OR ',
}
// map of pleiades urls to coordinates
var locations_dict = {};
// map of each facet to number of inscriptions with that particular facet
var facet_nums = {};

//////////////////////////////////////////////////////////////////////

// Setting up Basemap
var mymap = L.map('mapid').setView([31.3, 35.3], 7)

var base_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
    attribution: 'Map data &copy; <a href="https://openstreetmap.org">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://mapbox.com">Mapbox</a>',
        maxZoom: 11,
        id: 'isawnyu.map-knmctlkh',
        accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
    }).addTo(mymap);


// FUNCTIONS

// Called on map initialization to create map of pleiades urls to coordinate points
function createLocationsDict() {
  var promises = [];
  $.getJSON(LOCATIONS_URL, function(data) {
    $.each(data.facet_counts.facet_fields.city_pleiades, function(index, value) {
      if(index%2 === 0) {
        if (value.slice(-6) === "380758") {
          console.log("The 9-digit pleiades ID still has not been corrected.");
          value = "https://pleiades.stoa.org/places/678006";
        } else if (value.slice(0, 7) === "Maresha") {
          console.log("Invalid pleiades urls still present.");
          return false
        } else if (value.slice(-6) === "87966/"){
          return false
        }

        var promise = $.getJSON('https://pleiades.stoa.org/places/' + value.slice(-6) + '/json', function(data) {
          if (data.reprPoint) {
            locations_dict[value] = [data.reprPoint[1], data.reprPoint[0]];
            // console.log(locations_dict[value])
          } else {
            console.log("This inscription with pleiades ID " + value.slice(-6) + " has no coordinate value.");
          }
        });

        promises.push(promise);

      }
    });

    $.when.apply($, promises)
    .always(function() {
        createPointsLayer(BASE_URL);
    });

  });
};

// adds filters and concatenation operator (AND/OR) to FILTERS_URL
function addFiltersToUrl() {
  var query = '';
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length) {
      console.log("This filter has been applied: ", filters[filter]);
      var op = ops[filter];
      var str = '('
      for (var i = 0; i < filters[filter].length; i++) {
        str = str.concat(filter + ':"' + filters[filter][i] + '"' + op);
      }
      str = str.slice(0, -4);
      str = encodeURIComponent(str.concat(')'));
      console.log("This is the string for the filter: " + str);
      query = query.concat(str + ' AND ');
    }
  }
  query = query.slice(0, -4);
  console.log("This is the final query: " + query);
  var url = FILTERS_URL.concat(query);

  createPointsLayer(url);
}


//CLEAN UP THIS FUNCTION
// creates the points layer that shows up on the map
// url: the url to get the point data from
function createPointsLayer(url) {
  $('input:checkbox').attr('disabled', true)
  console.log("url: ", url);
  points_layer.clearLayers();
  facet_nums = {};

  $.getJSON(url, function(data) {
    console.log(data['grouped']['city_pleiades']['matches']);
    $.each(data['grouped']['city_pleiades']['groups'], function(index, point) {
      if (this.groupValue) {
        var coordinates = locations_dict[this.groupValue];
        if (coordinates) {
          var num_inscriptions = this['doclist']['numFound'];
          var place = this['doclist']['docs'][0]['city'];
          var region = this['doclist']['docs'][0]['region'];
          var placeMenu = this['doclist']['docs'][0]['placeMenu'];
          var p = L.circleMarker(coordinates, {
            region: region,
            place: place,
            num_inscriptions: num_inscriptions,
            radius: Math.sqrt(num_inscriptions) + 5,
            color: '#D15E28',
            weight: 2,
            pane: 'markerPane'
          });
          var inscriptions = {};
          for (var i = 0; i < this['doclist']['docs'].length; i++) {
            var doc = this['doclist']['docs'][i];
            inscriptions[doc.inscription_id] = {
              notBefore: doc['notBefore'],
              notAfter: doc['notAfter'],
              placeMenu: doc['placeMenu'],
              language: doc['language'], // LANGUAGE IS DELIMITED BY COMMAS SO ARRAY LENGTH >= 1
              language_display: doc['language_display'],
              religion: doc['religion'], // RELIGION IS DELIMITED BY COMMAS SO ARRAY LENGTH >= 1
              material: doc['material']
            };
            var inscription = inscriptions[doc.inscription_id];

            // TYPE IS DELIMITED BY SPACES SO ARRAY LENGTH = 1 (MUST SPLIT!!!)
            if (doc['type']) {
              inscription['type'] = doc['type'][0].split(/[\s,]+/);
            }
            // PHYSICAL_TYPE IS DELIMITED BY SPACES SO ARRAY LENGTH = 1 (MUST SPLIT!!!)
            if (doc['physical_type']) {
              inscription['physical_type'] = doc['physical_type'][0].split(/[\s,]+/);
            }
          }

          p.options.inscriptions = inscriptions;
          points_layer.addLayer(p);
        } else {
          // console.log("This key has no value in locations_dict: " + this.groupValue);
        }
      } else {
        docs_no_pleiades = this['doclist']['docs'];
        var coordinates_no_pleiades = {};
        $.each(docs_no_pleiades, function(index, doc) {
          inscription_id = doc['inscription_id']
          if (coordinates_no_pleiades.hasOwnProperty(doc['city_geo'])) {
            coordinates_no_pleiades[doc['city_geo']]['num_inscriptions'] += 1;
          } else {
            coordinates_no_pleiades[doc['city_geo']] = {
              num_inscriptions: 1,
              region: doc['region'],
              place: doc['city'],
              inscriptions: {}
            };
          }

          coordinates_no_pleiades[doc['city_geo']]['inscriptions'][inscription_id] = {
            notBefore: doc['notBefore'],
            notAfter: doc['notAfter'],
            placeMenu: doc['placeMenu'],
            language: doc['language'], // LANGUAGE IS DELIMITED BY COMMAS SO ARRAY LENGTH >= 1
            language_display: doc['language_display'],
            religion: doc['religion'], // RELIGION IS DELIMITED BY COMMAS SO ARRAY LENGTH >= 1
            material: doc['material']
          };

          var inscription = coordinates_no_pleiades[doc['city_geo']]['inscriptions'][inscription_id];

          // TYPE IS DELIMITED BY SPACES SO ARRAY LENGTH = 1 (MUST SPLIT!!!)
          if (doc['type']) {
            inscription['type'] = doc['type'][0].split(/[\s,]+/);
          }
          // PHYSICAL_TYPE IS DELIMITED BY SPACES SO ARRAY LENGTH = 1 (MUST SPLIT!!!)
          if (doc['physical_type']) {
            inscription['physical_type'] = doc['physical_type'][0].split(/[\s,]+/);
          }
        });
        $.each(coordinates_no_pleiades, function(key, value) {
          if (key == 'undefined') {
            console.log("Inscriptions no coordinates: ")
            console.log(value)
            return;
          }
          coordinates = key.split(',').map(Number);
          var p = L.circleMarker(coordinates, {
            region: value['region'],
            place: value['place'],
            num_inscriptions: value['num_inscriptions'],
            radius: Math.sqrt(value['num_inscriptions']) + 5,
            color: '#D15E28',
            weight: 2,
            pane: 'markerPane'
          });

          p.options.inscriptions = value['inscriptions'];
          points_layer.addLayer(p);
        });
      }
    });
    filterByDateRange();
    points_layer.addTo(mymap);
    $('input:checkbox').removeAttr('disabled')
  });
}


// increment numerical value corresponding to number of inscriptions with a
// particular facet field
function addFacetNums(inscription, facet_nums) {
  /* called by filterByDateRange() */
  if( inscription["placeMenu"][0].indexOf("Caesarea") > -1 ) {
    console.log( "addFacetNums() inscription, " + JSON.stringify(inscription) );
  }
  // console.log( 'facet_nums started, ' + JSON.stringify(facet_nums) )
  $.each(inscription, function(key, value) {
    if( inscription["placeMenu"][0].indexOf("Caesarea") > -1 ) {
      if(key == "placeMenu") {
        console.log( "value, " + value );
        // console.log( "facet_nums[value], " + facet_nums[value] );
      }
    }
    if ((key === 'language' || key === 'religion'|| key === 'type'
      || key === 'physical_type' || key === 'placeMenu' || key === 'material') && value) {
      for (var i = 0; i < value.length; i++) {
        if( inscription["placeMenu"][0].indexOf("Caesarea") > -1 ) {
          if(key == "placeMenu") {
            console.log( "i, " + i );
            console.log( "value.length, " + value.length );
            console.log( "facet_nums[value[i]], " + facet_nums[value[i]] );
          }
        }
        if (facet_nums[value[i]] === undefined) {
          facet_nums[value[i]] = 1;
        } else {
          facet_nums[value[i]] += 1;
        }

        // if( inscription["placeMenu"][0].indexOf("Caesarea") > -1 ) {
        //   if(key == "placeMenu") {
        //     console.log( "value, " + value );
        //   }
        // }

      }
    }
  });
  // console.log( 'facet_nums now, ' + JSON.stringify(facet_nums) )
  return true;
}


// // increment numerical value corresponding to number of inscriptions with a
// // particular facet field
// function addFacetNums(inscription, facet_nums) {
//   /* called by filterByDateRange() */
//   // console.log( 'facet_nums was, ' + JSON.stringify(facet_nums) )
//   $.each(inscription, function(key, value) {
//     // console.log( 'inscription, ' + inscription )
//     if ((key === 'language' || key === 'religion'|| key === 'type'
//       || key === 'physical_type' || key === 'placeMenu' || key === 'material') && value) {
//       for (var i = 0; i < value.length; i++) {
//         if (facet_nums[value[i]] === undefined) {
//           facet_nums[value[i]] = 1;
//         } else {
//           facet_nums[value[i]] += 1;
//         }
//       }
//     }
//   });
//   // console.log( 'facet_nums now, ' + JSON.stringify(facet_nums) )
//   return true;
// }

// update the numbers that show up to each facet in the filter menus
function updateSelectMenus() {
  $('.checkbox-default').each(function(index, checkbox){
    var input = $(checkbox).children('input');
    var value = input.val();
    // console.log( 'value, ' + value );
    var name = input.attr('name');
    // console.log( 'name, ' + name );
    if ($('input[name=' + name + '_]:checked').val() === 'and') {
      if (facet_nums.hasOwnProperty(value)) {
        $(this).find('span').text('('+facet_nums[value]+')');
      } else {
        $(this).find('span').text('(0)');
      }
    } else {
      if (facet_nums.hasOwnProperty(value)) {
        if (filters[name].length === 0 || input.is(':checked')) { //no filter for particular field
          $(this).find('span').text('('+facet_nums[value]+')');
        }
      } else {
        if (filters[name].length === 0 || input.is(':checked')) {
          $(this).find('span').text('(0)');
        }
      }
    }
  });

  disableEnableCheckboxes();
}

// disable or enable checkboxes if select multiple is on for a particuar filter
function disableEnableCheckboxes() {
  for (op in ops) {
    if (ops.hasOwnProperty(op) && ops[op] === ' AND ') {
      $('#' + op + '-filter input').each(function() {
        var str = $(this).siblings('label').children('span').text().slice(1, -1);
        if (str == '0') {
          $(this).prop('disabled', 'true');
        } else {
          $(this).removeAttr('disabled');
        }
      });
    }
  }
}

// change the radius of points on map depending on number of inscriptions in slider range
// num_in_range: number of inscriptions in slider range at a particular point
function changeRadius(num_in_range) {
  if (num_in_range > 0) {
    return Math.sqrt(num_in_range) + 5
  } else {
    return 0;
  }
}

// checks if any of the filter fields are checked after a change occurs in the menus
function hasFilters() {
  var has = true;
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length > 0) {
      addFiltersToUrl();
      return;
    }
  }

  createPointsLayer(BASE_URL);
}

// computers the string displayed on the slider corresponding to the slider's location
// value: the location of the slider
function computeSliderValue(value) {
  if (value > 0) {
    return value + " CE";
  } else if (value < 0) {
    return value * (-1) + " BCE";
  } else {
    return value;
  }
}

// updates the number in the the date textfield corresponding to the location of the slider
// slider_value: either handle-low or handle-high depending on which box
// checkbox_id: the id in the html of the checkbox to be updated
function updateDateFieldValue(slider_value, checkbox_id) {
  if (slider_value > 0) {
    $('#' + checkbox_id + '_1').prop('checked', true);
    return slider_value;
  } else {
    $('#' + checkbox_id + '_0').prop('checked', true);
    return slider_value * (-1);
  }
}

// // filters the points on the map by the date range of the sliders
// // also updates the popup on the point to reflect correct number of inscriptions
// function filterByDateRange() {
//   var low = $('#slider-range').slider("option", "values")[0];
//   var high = $('#slider-range').slider("option", "values")[1]
//   facet_nums = {};
//   console.log( 'facet_nums just initialized' );
//   console.log( 'facet_nums, ' + JSON.stringify(facet_nums) );
//   var promises = [];
//   points_layer.eachLayer(function(point) {

//     var num_in_range = 0;
//     for (var j in point['options']['inscriptions']) {
//       var inscr =  point['options']['inscriptions'][j];
//       if(inscr['notBefore'] == null) {
//         inscr['notBefore'] = $("#slider-range").slider("option", "min")
//       }
//       if (inscr['notAfter'] == null) {
//         inscr['notAfter'] = $("#slider-range").slider("option", "max")
//       }
//       if ((inscr['notBefore'] >= low && inscr['notBefore'] < high)
//         || (inscr['notAfter'] <= high && inscr['notAfter'] > low)) {
//         num_in_range += 1;
//         promises.push(addFacetNums(inscr, facet_nums));
//       }
//     }
//     if (num_in_range === 0) {
//       point.setRadius(0);
//     } else {
//       point.setRadius(Math.sqrt(num_in_range) + 5);
//     }

//     point['options']['num_inscriptions'] = num_in_range;
//     point.bindPopup("<strong>Place: </strong>"
//         + point['options']['place'] + "<br><strong>Region: </strong>"
//         + point['options']['region'] + "<br><strong>Inscriptions: </strong>"
//         + num_in_range);
//     point.on('click', function() {
//       return showInscriptions(point['options']['inscriptions']);
//     });
//   });
//   console.log( 'at this point, facet_nums has been updatd, and the counts are wrong' );
//   console.log( 'facet_nums, ' + JSON.stringify(facet_nums) );

// filters the points on the map by the date range of the sliders
// also updates the popup on the point to reflect correct number of inscriptions
function filterByDateRange() {
  var low = $('#slider-range').slider("option", "values")[0];
  var high = $('#slider-range').slider("option", "values")[1]
  facet_nums = {};
  console.log( 'facet_nums just initialized' );
  console.log( 'facet_nums, ' + JSON.stringify(facet_nums) );
  var promises = [];
  points_layer.eachLayer(function(point) {

    if( point["options"]["place"].indexOf("Caesarea") > -1 ) {
        console.log( "found!" );
        console.log( "point, " + JSON.stringify(point) );
        console.log( "point data..." );
        console.log( point["options"]["place"] );
        console.log( point["options"]["region"] );
        console.log( point["options"]["num_inscriptions"] );
        console.log( "facet_nums before point processing, " + JSON.stringify(facet_nums) );
    }

    // if( Math.floor(Math.random() * 10) > 8 ) {
    //     console.log( 'gogogo' );
    //     console.log( 'point, ' + JSON.stringify(point) );
    //     console.log( "point data..." );
    //     console.log( point["options"]["place"] );
    //     console.log( point["options"]["region"] );
    //     console.log( point["options"]["num_inscriptions"] );

    // } else {
    //     console.log( 'stop' );
    //     1/0;
    // }

    var num_in_range = 0;
    for (var j in point['options']['inscriptions']) {
      var inscr =  point['options']['inscriptions'][j];
      if(inscr['notBefore'] == null) {
        inscr['notBefore'] = $("#slider-range").slider("option", "min")
      }
      if (inscr['notAfter'] == null) {
        inscr['notAfter'] = $("#slider-range").slider("option", "max")
      }

      if( point["options"]["place"].indexOf("Caesarea") > -1 ) {
        // console.log( "inscr, " + JSON.stringify(inscr) );
        console.log( "num_in_range, " + num_in_range );
      }

      if ((inscr['notBefore'] >= low && inscr['notBefore'] < high)
        || (inscr['notAfter'] <= high && inscr['notAfter'] > low)) {
        num_in_range += 1;
        promises.push(addFacetNums(inscr, facet_nums));
      }
    }
    if (num_in_range === 0) {
      point.setRadius(0);
    } else {
      point.setRadius(Math.sqrt(num_in_range) + 5);
    }

    point['options']['num_inscriptions'] = num_in_range;
    point.bindPopup("<strong>Place: </strong>"
        + point['options']['place'] + "<br><strong>Region: </strong>"
        + point['options']['region'] + "<br><strong>Inscriptions: </strong>"
        + num_in_range);
    point.on('click', function() {
      return showInscriptions(point['options']['inscriptions']);
    });
  });
  console.log( 'at this point, facet_nums has been updatd, and the counts are wrong' );
  console.log( 'facet_nums, ' + JSON.stringify(facet_nums) );

  Promise.all(promises)
    .then((results) => {
      updateSelectMenus();
    })
    .catch((e) => {
      console.log("ERROR")
      console.log(e);
    });
}

// updates the filters map once a checkbox in one of the menus changes
// filter: the type of the filter to be updated (i.e. place, type, physical_type, etc.)
function updateFilters(filter) {
  var selected = $('#' + filter + '-filter input:checked');
  filters[filter] = [];
  selected.each(function() {
    console.log('filter', $(this))
    filters[filter].push($(this).val());
  });
  hasFilters();
}

// shows inscriptions in the map-inscriptions-box when a point on the map is clicked
// the inscriptions located at the selected point
function showInscriptions(inscriptions) {
  $('#map-inscriptions-box ul').empty();
  for (inscription in inscriptions) {
    if (inscriptions.hasOwnProperty(inscription)) {
      $('#map-inscriptions-box ul').prepend('<li class="inscription" id=' + inscription + '><label><a href="../viewinscr/'
        + inscription + '" target="_blank">' + inscription.toUpperCase().substr(0,4) + ' ' + inscription.substr(4) + '</a>'
        + '</label></li>');
      var inscr = inscriptions[inscription];
      if (inscr['type'] === undefined || inscr['type'][0].trim() === '') {
        $('#' + inscription).append('<br>Type: N/A');
      } else {
        $('#' + inscription).append('<br>Type: ' + inscr['type']);
      }

      if (inscr['physical_type'] === undefined || inscr['physical_type'][0].trim() === '') {
        $('#' + inscription).append('<br>Physical Type: N/A');
      } else {
        $('#' + inscription).append('<br>Physical Type: ' + inscr['physical_type']);
      }

      if (inscr['language'] === undefined || inscr['language'][0].trim() === '') {
        $('#' + inscription).append('<br>Language: N/A');
      } else {
        $('#' + inscription).append('<br>Language: ' + inscr['language_display']);
      }

      if (inscr['religion'] === undefined || inscr['religion'][0].trim() === '') {
        $('#' + inscription).append('<br>Religion: N/A');
      } else {
        $('#' + inscription).append('<br>Religion: ' + inscr['religion']);
      }

      if (inscr['material'] === undefined || inscr['material'][0].trim() === '') {
        $('#' + inscription).append('<br>Material: N/A');
      } else {
        $('#' + inscription).append('<br>Material: ' + inscr['material']);
      }
    }
  }
}

// highlights a region of an overlay on mouseover
function highlightRegion(e) {
    var layer = e.target;
    layer.setStyle({
        weight: 3,
        color: '#666',
        dashArray: '',
        fillOpacity: 0.7
    });

    layer.openTooltip();

    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
        layer.bringToFront();
    }
}

// function for applying functionality to roman provinces overlay
function onEachRomanProvince(feature, layer) {
  layer.bindTooltip('<strong>Roman Province</strong><br>' + feature.properties.province, {sticky: true, direction: 'center', offset: [0, 18], className: 'roman-province tooltip'});
  layer.on({
      mouseover: highlightRegion,
      mouseout: function() {
        layer.closeTooltip();
        roman_provinces.resetStyle(layer);
      }
  });
}

// function for applying functionality to byzantine provinces overlay
function onEachByzantine(feature, layer) {
  layer.bindTooltip('<strong>Byzantine Province</strong><br>' + feature.properties.Name, {sticky: true, direction: 'center', offset: [0, 18], className: 'byzantine-province tooltip'});
  layer.on({
      mouseover: highlightRegion,
      mouseout: function() {
        layer.closeTooltip();
        byzantine_provinces_400CE.resetStyle(layer);
      }
  });
}

// function for applying highlighting functionality to IIP regions overlay
function onEachIIP(feature, layer) {
  layer.bindTooltip('<strong>IIP Region</strong><br>' + feature.properties.Name, {sticky: true, direction: 'center', offset: [0, 18], className: 'iip-region tooltip'});
  layer.on({
    mouseover: highlightRegion,
    mouseout: function() {
      layer.closeTooltip();
      iip_regions.resetStyle(layer);
    }
  });
}

function onEachKingHerod(feature, layer) {
  layer.bindTooltip('<strong>King Herod Boundary</strong><br>' + feature.properties.Name, {sticky: true, direction: 'center', offset: [0, 18], className: 'iip-region tooltip'});
  layer.on({
    mouseover: highlightRegion,
    mouseout: function() {
      layer.closeTooltip();
      king_herod_boundaries_37BCE.resetStyle(layer);
    }
  });
}

// adds and removes overlays on map
function toggleOverlay(overlay) {
  if (mymap.hasLayer(overlay)) {
    mymap.removeLayer(overlay);
  } else {
    mymap.addLayer(overlay);
  }
}


// OVERLAYS

var roman_provinces;
var roman_roads;
var byzantine_provinces_400CE;
var iip_regions;
var king_herod_boundaries_37BCE;

// ajax call for getting overlay data
$.ajax({
  dataType: "json",
  url: "load_layers",
  success: function(data) {

    var provinces = JSON.parse(data.roman_provinces);
    roman_provinces = new L.geoJSON(provinces, {color: 'olive', weight: 1, onEachFeature: onEachRomanProvince});

    var roads = JSON.parse(data.roman_roads);
    roman_roads = new L.geoJSON(roads, {style: getWeight});

    var byzantine = JSON.parse(data.byzantine_provinces_400CE);
    byzantine_provinces_400CE = new L.geoJSON(byzantine, {color: 'gray', weight: 1, onEachFeature: onEachByzantine});

    var iip = JSON.parse(data.iip_regions);
    iip_regions = new L.geoJSON(iip, {color: 'navy', weight: 1, onEachFeature: onEachIIP});

    var king_herod = JSON.parse(data.king_herod);
    king_herod_boundaries_37BCE = new L.geoJSON(king_herod, {color: 'brown', weight: 1, onEachFeature: onEachKingHerod});
  }
});


// FUNCTION FOR CHANGING ROAD WEIGHTS
var getWeight = function(road) {
  var line_weight;
  var dash_array;
  var color;

  if (road.properties.Major_or_M === "0") {
    line_weight = 1;
  } else {
    line_weight = 2;
  }

  if (road.properties.Known_or_a) {
    dash_array = null;
  } else {
    dash_array = '1 5';
  }

  return {weight: line_weight, dashArray: dash_array, color: 'maroon'}
}

// CHECKBOXES IN OVERLAY MENU

$('#roman_provinces').click(function() {
  return toggleOverlay(roman_provinces);
});

$('#roman_roads').click(function() {
  return toggleOverlay(roman_roads);
});

$('#byzantine_provinces_400CE').click(function() {
  return toggleOverlay(byzantine_provinces_400CE);
});

$('#iip_regions').click(function(){
  return toggleOverlay(iip_regions);
});

$('#king_herod_boundaries_37BCE').click(function(){
  return toggleOverlay(king_herod_boundaries_37BCE);
});

var satelite_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
    attribution: 'satelite',
        maxZoom: 11,
        id: 'mapbox.satellite',
        accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
    });

$('#overlay_satelite').click(function(){
  if (mymap.hasLayer(base_tile)){
      mymap.removeLayer(base_tile);
      satelite_tile.addTo(mymap);
      console.log("satelite view on");
  } else {
      mymap.removeLayer(satelite_tile);
      base_tile.addTo(mymap);
      console.log("satelite view off");
  }
});



//{% if inscriptions[inscription]['material'] %}inscriptions[inscription]['material']{%else%}Not Available{% endif %}


// SLIDER

var handle1 = $( "#custom-handle-low" );
var handle2 = $( "#custom-handle-high"  );
$("#slider-range").slider({
    range: true,
    min: -600,
    max: 650,
    values: [-600, 650],
    step:1,
    create: function() {
      handle1.text("600 BCE");
      handle2.text("650 CE");
    },
    slide: function( event, ui ) {
      handle1.text(computeSliderValue(ui.values[0]));
      handle2.text(computeSliderValue(ui.values[1]));
      $('#id_notBefore').val(updateDateFieldValue(ui.values[0], 'id_afterDateEra'));
      $('#id_notAfter').val(updateDateFieldValue(ui.values[1], 'id_beforeDateEra'));
      filterByDateRange();
    }
});


// FILTER CHECKBOX CHANGES

$('#place-filter').change(function() {
  return updateFilters('place');
});

$('#type-filter').change(function() {
  return updateFilters('type');
});

$('#physical_type-filter').change(function() {
  return updateFilters('physical_type');
});

$('#language-filter').change(function() {
  return updateFilters('language');
});

$('#religion-filter').change(function() {
  return updateFilters('religion');
});

$('#material-filter').change(function() {
  return updateFilters('material');
});


// BUTTONS

$("input[type='radio']").click(function() {
  var filter = $(this).attr('name').slice(0, -1);
  console.log("filter", filter)
  if ($(this).val() === ("and")) {
    $('#'+filter+'-filter > .checkbox.checkbox-default').each(function(index, checkbox) {
      this.classList.add('checkbox-circle');
      $(this).children('input').prop('checked', false);
    });
    ops[filter] = ' AND ';
    filters[filter] = []
  } else {
    $('#'+filter+'-filter > .checkbox.checkbox-default').each(function(index, radio) {
      this.classList.remove('checkbox-circle');
      $(this).children('input').attr('disabled', false);
    });
    ops[filter] = ' OR ';
  }
  hasFilters();
});

$("#points_layer").click(function() {
  if(mymap.hasLayer(points_layer)) {
    mymap.removeLayer(points_layer);
    $(this).text("Show Points");
  } else {
    mymap.addLayer(points_layer);
    $(this).text("Hide Points");
  }
});

$('#advanced_detail').click(function(){
    var advanced_search = document.getElementById("advanced_search");
    advanced_search.style.display = advanced_search.style.display == "block" ? "none" : "block";
    return false;
});

$('#reset').click(function() {
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length > 0) {
      filters[filter] = [];
    }
    $('#'+filter+'-filter > .checkbox.checkbox-default').each(function(index, radio) {
      this.classList.remove('checkbox-circle');
      $(this).children('input').attr('disabled', false);
    });
  }
  ops = {
    place: ' OR ',
    type: ' OR ',
    physical_type: ' OR ',
    language: ' OR ',
    religion: ' OR ',
    material: ' OR ',
  }
  $('#map-inscriptions-box ul').empty();
  $("#slider-range").slider('values', 0, -600);
  handle1.text("600 BCE");
  $("#slider-range").slider('values', 1, 650);
  handle2.text("650 CE");
  createPointsLayer(BASE_URL);
});


$('.checkbox-default').each(function(index, checkbox) {
  var input = $(checkbox).find('input');
  $(checkbox).prepend(input);
});

$('.filter-container label').each(function(index) {
  $(this).append('<span class="facet-count"></span>');
});

$(':checkbox').each(function() {
  $(this).prop('checked', false);
});

createLocationsDict();
