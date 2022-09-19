// for console.logging
function timestamp() {
    let d = new Date();
    let time_string = d.toLocaleTimeString();
    // return time_string;
    return "debug";
};


// GLOBAL VARS

/* base url for getting all inscriptions */
// var BASE_URL = 'https://library.brown.edu/cds/projects/iip/api/?start=0&rows=6000&indent=on&fl=inscription_id,region,city,city_geo,notBefore,notAfter,placeMenu,type,physical_type,language,language_display,religion,material&wt=json&group=true&group.field=city_pleiades&group.limit=-1&q=*:*';
// Note: API_URL is set in `mapsearch.html`` template, just before mapsearch.js is loaded
var BASE_URL = API_URL + "?start=0&rows=6000&indent=on&fl=inscription_id,region,city,city_geo,notBefore,notAfter,placeMenu,type,physical_type,language,language_display,religion,material&wt=json&group=true&group.field=city_pleiades&group.limit=-1&q=*:*";
// console.log( "BASE_URL: ", BASE_URL );
console.log( timestamp(), "[global]", "BASE_URL,", BASE_URL )

/* url for applying filters to base url */
var FILTERS_URL = BASE_URL.concat("&fq=");
console.log( timestamp(), "[global]", "FILTERS_URL,", FILTERS_URL )

/* url for getting all pleiades urls from database */
// var LOCATIONS_URL = 'https://library.brown.edu/cds/projects/iip/api/?q=*:*&%3A*&start=0&rows=0&indent=on&facet=on&facet.field=city_pleiades&wt=json';
// Note: API_URL is set in `mapsearch.html`` template, just before mapsearch.js is loaded
var LOCATIONS_URL = API_URL + "?q=*:*&%3A*&start=0&rows=0&indent=on&facet=on&facet.field=city_pleiades&wt=json";
console.log( timestamp(), "[global]", "LOCATIONS_URL,", LOCATIONS_URL )
// console.log( "LOCATIONS_URL: ", LOCATIONS_URL );

// layer of points for inscriptions on map
var points_layer = L.layerGroup();

let facet_nums_request = {}

// map of each type of filters and the specific filter names that are being applied (e.g. place: ['Coastal Plain', 'Golan'])
var filters = {
  placeMenu: [],
  type: [],
  physical_type: [],
  language: [],
  religion: [],
  material: []
};

// map of concatenators for multiple filters. default is 'OR' unless set to AND
var ops = {
  // place: ' OR ',
  type: ' OR ',
  physical_type: ' OR ',
  language: ' OR ',
  religion: ' OR ',
  material: ' OR ',
  placeMenu: 'OR',
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

async function requestFacetNums(ops_request, request_url) {
  //console.log('requestFacetNums', ops_request, request_url)
  console.log( timestamp(), "[requestFacetNums()]", "starting" );
  content_array = new Array();

  //Make sure we're not asking for item-level data here. 
  //TODO: Refactor this script and use a less hacky way to do this.
  request_url = request_url.replace(/rows=\d+&/, 'rows=0&');
  request_url += Object.keys(ops_request).join('&facet.field=');

  await $.ajax({
    
    url: request_url,
    dataType: 'json',
    success: function (data) {
      // console.log("DEGUG@Yang@3\t", field, JSON.stringify(data.facet_counts.facet_fields[field]));
      console.log( timestamp(), "[requestFacetNums()]", "data,", data );
      for (field in ops_request) {
        let raw_array = data.facet_counts.facet_fields[field];
        let key_value_dict = {};
        // console.log(raw_array);
        for (let i = 0; i < raw_array.length - 1; i += 2) {
          key_value_dict[raw_array[i]] = raw_array[i + 1];
        }
        content_array.push(key_value_dict);
        //console.log('requestFacetNums output:', raw_array, key_value_dict);
      }
    }
  });
  // console.log( timestamp(), "[requestFacetNums()]", "bar" );
  return content_array;
}

async function initializeFacetNums(request_url, date_query) {
  console.log( timestamp(), "[initializeFacetNums()]", "starting" );
  console.log( timestamp(), "[initializeFacetNums()]", "request_url", request_url );
  console.log( timestamp(), "[initializeFacetNums()]", "date_query", date_query );
  // console.log('debug', 'initializeFacetNums', request_url, date_query);
  let ops_request = {
    // place: ' OR ',
    type: ' OR ',
    physical_type: ' OR ',
    language: ' OR ',
    religion: ' OR ',
    material: ' OR ',
    placeMenu: 'OR',
  };
  if (request_url === 'default') {
    // request_url = 'https://library.brown.edu/cds/projects/iip/api/?start=0&rows=0&indent=on&fl=type&q=*:*&facet=on&facet.field=';
    request_url = API_URL + "?start=0&rows=0&indent=on&fl=type&q=*:*&facet=on&facet.field=";  // API_URL is set in `mapsearch.html`` template, just before mapsearch.js is loaded
    console.log( timestamp(), "[initializeFacetNums()]", "request_url,", request_url );
  } else {
    if (date_query === '(notBefore:[-600 TO 10000]) AND (notAfter:[-10000 TO 650])') {
      // this is the default date range, so query should be null
      date_query = '*:*';
    }
    if (request_url.includes('q=*:*')) {
      request_url = request_url.replace('q=*:*', 'q=' + date_query);
    }
    if (!request_url.includes('facet=on&facet.field=')) {
      console.log("facet=on&facet.field= not in request_url, program will add these.");
      request_url = request_url + '&facet=on&facet.field=';
      // you shall always keep "facet.field=" in the ending of the query url
    }
  }
  let content_array = await requestFacetNums(ops_request, request_url);
  console.log("DEBUG@initializeFacetNums request_url", request_url);
  // console.log("DEBUG@initializeFacetNums", content_array);
  facet_nums_request = Object.assign({}, content_array[0], content_array[1],
    content_array[2], content_array[3], content_array[4], content_array[5]);
  return facet_nums_request;
}

// Called on map initialization to create map of pleiades urls to coordinate points
async function createLocationsDict() {
  console.log( timestamp(), "[createLocationsDict()]", "starting; about to call initializeFacetNums()" );
  facet_nums_request = await initializeFacetNums('default');
  console.log('DEBUG@createLocationsDict facet_nums_request', facet_nums_request);
  var promises = [];
  $.getJSON(LOCATIONS_URL, function (data) {
    $.each(data.facet_counts.facet_fields.city_pleiades, function (index, value) {
      if (index % 2 === 0) {
        if (value.slice(-6) === "380758") {
          console.log("The 9-digit pleiades ID still has not been corrected.");
          value = "https://pleiades.stoa.org/places/678006";
        } else if (value.slice(0, 7) === "Maresha") {
          console.log("Invalid pleiades urls still present.");
          return false
        } else if (value.slice(-6) === "87966/") {
          return false
        }
        var promise = $.getJSON('https://pleiades.stoa.org/places/' + value.slice(-6) + '/json', function (data) {
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
      .always(function () {
        createPointsLayer(BASE_URL);
      });
  });
};



// adds filters and concatenation operator (AND/OR) to FILTERS_URL
async function addFiltersToUrl() {
  var query = '';
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length) {
      console.log("This filter has been applied: ", filters[filter]);
      var op = ops[filter];
      let str_filter = '('
      let i = 0
      for (; i < filters[filter].length - 1; i++) {
        str_filter = str_filter.concat(filter + ':"' + filters[filter][i] + '"' + op);
      }
      str_filter = str_filter.concat(filter + ':"' + filters[filter][i] + '"');

      str_filter = encodeURIComponent(str_filter.concat(')'));
      query = query.concat(str_filter + ' AND ');
    }
  }

  query = query.slice(0, -4);
  var url = FILTERS_URL.concat(query);
  await createPointsLayer(url);
}

//CLEAN UP THIS FUNCTION
// creates the points layer that shows up on the map
// url: the url to get the point data from
async function createPointsLayer(url) {
  $('input:checkbox').attr('disabled', true)
  points_layer.clearLayers();
  date_query = filterByDateRangeNumbers();
  // add date into query
  console.log('DEBUG@createPointsLayer: url', url);
  console.log('DEBUG@createPointsLayer: date_query', date_query);
  facet_nums_request = await initializeFacetNums(url, date_query);

  $.getJSON(url, function (data) {
    console.log(data['grouped']['city_pleiades']['matches']);
    console.log("DEBUG,data['grouped']['city_pleiades']['groups']", data['grouped']['city_pleiades']['groups']);
    $.each(data['grouped']['city_pleiades']['groups'], function (index, point) {
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
          if (this['doclist']['docs'][0]['type'] == 'legal') {
            console.log("DEBUG:This key has no value in locations_dict: ", this['doclist']['docs'][0]);
          }
        }
      } else {
        docs_no_pleiades = this['doclist']['docs'];
        var coordinates_no_pleiades = {};
        $.each(docs_no_pleiades, function (index, doc) {
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

        $.each(coordinates_no_pleiades, function (key, value) {
          console.log("DEBUG, coordinates_no_pleiades", coordinates_no_pleiades);
          if (key == 'undefined') {
            console.log("Inscriptions no coordinates: ");
            console.log(value['inscriptions']);
            for (k in value['inscriptions']) {
              if (value['inscriptions'][k]['type']['0'] === 'prayer')
                console.log('Inscriptions no coordinates:', Object.keys(value['inscriptions'][k]['type']));
            }
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

// update the numbers that show up to each facet in the filter menus
function updateSelectMenus() {
  // facet_nums = facet_nums_request;
  // console.log('DEBUG:updateSelectMenus@facet_nums properties', facet_nums_request);
  $('.checkbox-default').each(function (index, checkbox) {
    var input = $(checkbox).children('input');
    var value = input.val();
    // console.log('DEBUG:updateSelectMenus@value, ' + value);
    var name = input.attr('name');
    if (name === 'place') {
      name = 'placeMenu';
    }
    // console.log('DEBUG:updateSelectMenus@name, ' + name);
    if ($('input[name=' + name + '_]:checked').val() === 'and') {
      // console.log('DEBUG:updateSelectMenus@\tAND');
      if (facet_nums_request.hasOwnProperty(value)) {
        $(this).find('span').text('(' + facet_nums_request[value] + ')');
      } else {
        $(this).find('span').text('(0)');
      }
    } else {
      // console.log('DEBUG:updateSelectMenus@\tOR')
      if (facet_nums_request.hasOwnProperty(value)) {
        // console.log('DEBUG:updateSelectMenus@filed_value facet_nums.hasOwnProperty', value)
        if (filters[name].length === 0 || input.is(':checked')) { //no filter for particular field
          $(this).find('span').text('(' + facet_nums_request[value] + ')');
        }
      } else {
        // console.log('DEBUG:updateSelectMenus@filed_value ', value)
        if (filters[name].length === 0 || input.is(':checked')) {
          $(this).find('span').text('(0)');
        }
      }
    }
    // facet_nums = facet_nums_request;
  });

  disableEnableCheckboxes();
}

// disable or enable checkboxes if select multiple is on for a particuar filter
function disableEnableCheckboxes() {
  for (op in ops) {
    if (ops.hasOwnProperty(op) && ops[op] === ' AND ') {
      $('#' + op + '-filter input').each(function () {
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
    console.log('DEBUG@hasFilters ', filters.hasOwnProperty(filter));
    console.log('DEBUG@hasFilters', filters[filter]);
    if (filters.hasOwnProperty(filter) && filters[filter].length > 0) {
      console.log('DEBUG@hasFilters 1');
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


function parseDateYear(year) {
  if (year.includes('BCE')) {
    result = -1 * parseInt(year.slice(0, -4));
  } else if (year.includes('CE')) {
    result = parseInt(year.slice(0, -3));
  }
  return result;
}

function filterByDateRangeNumbers() {
  var date1 = $('#slider-range > #custom-handle-low').text();
  var date2 = $('#slider-range > #custom-handle-high').text();
  date1 = parseDateYear(date1);
  date2 = parseDateYear(date2);
  date_query = `(notBefore:[${date1} TO 10000]) AND (notAfter:[-10000 TO ${date2}])`;
  return date_query;
}

function filterByDateRange() {
  var low = $('#slider-range').slider("option", "values")[0];
  var high = $('#slider-range').slider("option", "values")[1]
  var promises = [];

  points_layer.eachLayer(function (point) {

    if (point["options"]["place"].indexOf("Caesarea") > -1) {
      console.log("found!");
      // console.log( "point, " + JSON.stringify(point) );
      console.log("point data...");
      console.log(point["options"]["place"]);
      console.log(point["options"]["region"]);
      console.log(point["options"]["num_inscriptions"]);
    }

    var num_in_range = 0;
    console.log("DEBUG:point['options']['inscriptions']", Object.values(point['options']['inscriptions']));
    for (var j in point['options']['inscriptions']) {
      var inscr = point['options']['inscriptions'][j];

      if (inscr['type'] == 'prayer')
        console.log('DEBUG:inscr type:prayer')

      if (inscr['notBefore'] == null) {
        inscr['notBefore'] = $("#slider-range").slider("option", "min")
      }
      if (inscr['notAfter'] == null) {
        inscr['notAfter'] = $("#slider-range").slider("option", "max")
      }

      // if( point["options"]["place"].indexOf("Caesarea") > -1 ) {
      //   // console.log( "inscr, " + JSON.stringify(inscr) );
      //   console.log( "num_in_range, " + num_in_range );
      // }

      if ((inscr['notBefore'] >= low && inscr['notBefore'] <= high)
        || (inscr['notAfter'] <= high && inscr['notAfter'] >= low)) {
        num_in_range += 1;
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
    point.on('click', function () {
      return showInscriptions(point['options']['inscriptions']);
    });
  });

  console.log('at this point, facet_nums has been updatd, and the counts are wrong');

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
  if (filter != 'placeMenu') {
    var selected = $('#' + filter + '-filter input:checked');
  } else {
    var selected = $('#' + 'place' + '-filter input:checked');
  }
  filters[filter] = [];
  selected.each(function () {
    console.log('DEBUG@updateFilters', $(this), $(this).val());
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
        + inscription + '" target="_blank">' + inscription.toUpperCase().substr(0, 4) + ' ' + inscription.substr(4) + '</a>'
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
  layer.bindTooltip('<strong>Roman Province</strong><br>' + feature.properties.province, { sticky: true, direction: 'center', offset: [0, 18], className: 'roman-province tooltip' });
  layer.on({
    mouseover: highlightRegion,
    mouseout: function () {
      layer.closeTooltip();
      roman_provinces.resetStyle(layer);
    }
  });
}

// function for applying functionality to byzantine provinces overlay
function onEachByzantine(feature, layer) {
  layer.bindTooltip('<strong>Byzantine Province</strong><br>' + feature.properties.Name, { sticky: true, direction: 'center', offset: [0, 18], className: 'byzantine-province tooltip' });
  layer.on({
    mouseover: highlightRegion,
    mouseout: function () {
      layer.closeTooltip();
      byzantine_provinces_400CE.resetStyle(layer);
    }
  });
}

// function for applying highlighting functionality to IIP regions overlay
function onEachIIP(feature, layer) {
  layer.bindTooltip('<strong>IIP Region</strong><br>' + feature.properties.Name, { sticky: true, direction: 'center', offset: [0, 18], className: 'iip-region tooltip' });
  layer.on({
    mouseover: highlightRegion,
    mouseout: function () {
      layer.closeTooltip();
      iip_regions.resetStyle(layer);
    }
  });
}

function onEachKingHerod(feature, layer) {
  layer.bindTooltip('<strong>King Herod Boundary</strong><br>' + feature.properties.Name, { sticky: true, direction: 'center', offset: [0, 18], className: 'iip-region tooltip' });
  layer.on({
    mouseover: highlightRegion,
    mouseout: function () {
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
  success: function (data) {

    var provinces = JSON.parse(data.roman_provinces);
    roman_provinces = new L.geoJSON(provinces, { color: 'olive', weight: 1, onEachFeature: onEachRomanProvince });

    var roads = JSON.parse(data.roman_roads);
    roman_roads = new L.geoJSON(roads, { style: getWeight });

    var byzantine = JSON.parse(data.byzantine_provinces_400CE);
    byzantine_provinces_400CE = new L.geoJSON(byzantine, { color: 'gray', weight: 1, onEachFeature: onEachByzantine });

    var iip = JSON.parse(data.iip_regions);
    iip_regions = new L.geoJSON(iip, { color: 'navy', weight: 1, onEachFeature: onEachIIP });

    var king_herod = JSON.parse(data.king_herod);
    king_herod_boundaries_37BCE = new L.geoJSON(king_herod, { color: 'brown', weight: 1, onEachFeature: onEachKingHerod });
  }
});


// FUNCTION FOR CHANGING ROAD WEIGHTS
var getWeight = function (road) {
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

  return { weight: line_weight, dashArray: dash_array, color: 'maroon' }
}

// CHECKBOXES IN OVERLAY MENU

$('#roman_provinces').click(function () {
  return toggleOverlay(roman_provinces);
});

$('#roman_roads').click(function () {
  return toggleOverlay(roman_roads);
});

$('#byzantine_provinces_400CE').click(function () {
  return toggleOverlay(byzantine_provinces_400CE);
});

$('#iip_regions').click(function () {
  return toggleOverlay(iip_regions);
});

$('#king_herod_boundaries_37BCE').click(function () {
  return toggleOverlay(king_herod_boundaries_37BCE);
});

var satelite_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
  attribution: 'satelite',
  maxZoom: 11,
  id: 'mapbox.satellite',
  accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
});

// $('#overlay_satelite').click(function () {
//   if (mymap.hasLayer(base_tile)) {
//     mymap.removeLayer(base_tile);
//     satelite_tile.addTo(mymap);
//     console.log("satelite view on");
//   } else {
//     mymap.removeLayer(satelite_tile);
//     base_tile.addTo(mymap);
//     console.log("satelite view off");
//   }
// });

  if (mymap.hasLayer(base_tile)) {
    mymap.removeLayer(base_tile);
    satelite_tile.addTo(mymap);
    // console.log("satelite view on");
    console.log( timestamp(), "[gobal]", "satelite view on"  );
  } else {
    mymap.removeLayer(satelite_tile);
    base_tile.addTo(mymap);
    console.log("satelite view off");
  }



//{% if inscriptions[inscription]['material'] %}inscriptions[inscription]['material']{%else%}Not Available{% endif %}


// SLIDER

var handle1 = $("#custom-handle-low");
var handle2 = $("#custom-handle-high");
$("#slider-range").slider({
  range: true,
  min: -600,
  max: 650,
  values: [-600, 650],
  step: 1,
  create: function () {
    handle1.text("600 BCE");
    handle2.text("650 CE");
  },
  slide: function (event, ui) {
    handle1.text(computeSliderValue(ui.values[0]));
    handle2.text(computeSliderValue(ui.values[1]));
    $('#id_notBefore').val(updateDateFieldValue(ui.values[0], 'id_afterDateEra'));
    $('#id_notAfter').val(updateDateFieldValue(ui.values[1], 'id_beforeDateEra'));
    filterByDateRange();
  },
  stop: function (event, ui) {
    addFiltersToUrl(); // this function will call createPointsLayer().
  }
});


// FILTER CHECKBOX CHANGES

$('#place-filter').change(function () {
  return updateFilters('placeMenu');
});

$('#type-filter').change(function () {
  return updateFilters('type');
});

$('#physical_type-filter').change(function () {
  return updateFilters('physical_type');
});

$('#language-filter').change(function () {
  return updateFilters('language');
});

$('#religion-filter').change(function () {
  return updateFilters('religion');
});

$('#material-filter').change(function () {
  return updateFilters('material');
});


// BUTTONS

$("input[type='radio']").click(function () {
  var filter = $(this).attr('name').slice(0, -1);
  console.log("filter", filter)
  if ($(this).val() === ("and")) {
    $('#' + filter + '-filter > .checkbox.checkbox-default').each(function (index, checkbox) {
      this.classList.add('checkbox-circle');
      $(this).children('input').prop('checked', false);
    });
    ops[filter] = ' AND ';
    filters[filter] = []
  } else {
    $('#' + filter + '-filter > .checkbox.checkbox-default').each(function (index, radio) {
      this.classList.remove('checkbox-circle');
      $(this).children('input').attr('disabled', false);
    });
    ops[filter] = ' OR ';
  }
  hasFilters();
});

$("#points_layer").click(function () {
  if (mymap.hasLayer(points_layer)) {
    mymap.removeLayer(points_layer);
    $(this).text("Show Points");
  } else {
    mymap.addLayer(points_layer);
    $(this).text("Hide Points");
  }
});

$('#advanced_detail').click(function () {
  var advanced_search = document.getElementById("advanced_search");
  advanced_search.style.display = advanced_search.style.display == "block" ? "none" : "block";
  return false;
});

$('#reset').click(function () {
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length > 0) {
      filters[filter] = [];
    }
    $('#' + filter + '-filter > .checkbox.checkbox-default').each(function (index, radio) {
      this.classList.remove('checkbox-circle');
      $(this).children('input').attr('disabled', false);
    });
  }
  ops = {
    placeMenu: ' OR ',
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


$('.checkbox-default').each(function (index, checkbox) {
  var input = $(checkbox).find('input');
  $(checkbox).prepend(input);
});

$('.filter-container label').each(function (index) {
  $(this).append('<span class="facet-count"></span>');
});

$(':checkbox').each(function () {
  $(this).prop('checked', false);
});

createLocationsDict();

var FACET_NUMBER_QUERY_API = '';

