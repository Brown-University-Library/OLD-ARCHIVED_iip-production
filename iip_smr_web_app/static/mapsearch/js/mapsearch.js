// GLOBAL VARS

var BASE_URL = 'http://library.brown.edu/cds/projects/iip/api/?start=0&rows=3278&indent=on&fl=inscription_id,region,city,city_geo,notBefore,notAfter,placeMenu,type,physical_type,language,language_display,religion,material&wt=json&group=true&group.field=city_pleiades&group.limit=-1&q=*:*';
var FILTERS_URL = BASE_URL.concat("&fq=");
var LOCATIONS_URL = 'http://library.brown.edu/cds/projects/iip/api/?q=*:*&%3A*&start=0&rows=0&indent=on&facet=on&facet.field=city_pleiades&wt=json';
var points_layer = L.layerGroup();
var filters = {
  place: [],
  type: [],
  physical_type: [],
  language: [],
  religion: [],
  material: []
}; 
var ops = {
  place: ' OR ',
  type: ' OR ',
  physical_type: ' OR ',
  language: ' OR ',
  religion: ' OR ',
  material: ' OR ',
}
var locations_dict = {};
var facet_nums = {};
var coordinates_no_pleiades = {};

////////////////////////////////////////////////////////////////////// 

// Setting up Basemap 
var mymap = L.map('mapid').setView([31.3, 35.3], 7)

var base_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
        maxZoom: 11,
        id: 'isawnyu.map-knmctlkh',
        accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
    }).addTo(mymap);


// BUTTONS
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
  }
  $('#map-inscriptions-box ul').empty();
  $("#slider-range").slider('values', 0, -600);
  handle1.text("600 BCE");
  $("#slider-range").slider('values', 1, 650);
  handle2.text("650 CE");
  createPointsLayer(BASE_URL);
})


// Called on map initialization
function createLocationsDict() {
  var promises = [];
  $.getJSON(LOCATIONS_URL, function(data) {
    $.each(data.facet_counts.facet_fields.city_pleiades, function(index, value) {
      if(index%2 === 0) {
        if (value.slice(-6) === "380758") {
          console.log("The 9-digit pleiades ID still has not been corrected.");
          value = "http://pleiades.stoa.org/places/678006";
        } else if (value.slice(0, 7) === "Maresha") {
          console.log("Invalid pleiades urls still present.");
          return false;
        }

        var promise = $.getJSON('https://pleiades.stoa.org/places/' + value.slice(-6) + '/json', function(data) {
          if (data.reprPoint) {
            locations_dict[value] = [data.reprPoint[1], data.reprPoint[0]];
          } else {
            console.log("This inscription with pleiades ID " + value.slice(-6) + " has no coordinate value.");
          }
        });

        promises.push(promise);
      }
    });

    $.when.apply($, promises)
    .done(function() {
        createPointsLayer(BASE_URL);
    });
  });  
};

function addFiltersToUrl(url_filters, url) {
  var query = '';
  for (var filter in url_filters) {
    if (url_filters.hasOwnProperty(filter) && url_filters[filter].length) {
      console.log("url_filters[filter].length: " + url_filters[filter].length)
      console.log("This filter has been applied: ", url_filters[filter]);
      var op = ops[filter];
      var str = '('
      for (var i = 0; i < url_filters[filter].length; i++) {
        str = str.concat(filter + ':"' + url_filters[filter][i] + '"' + op);
      }
      str = str.slice(0, -4);
      str = encodeURIComponent(str.concat(')'));
      console.log("This is the string for the filter: " + str);
      query = query.concat(str + ' AND ');
    }
  }
  query = query.slice(0, -4);
  console.log("This is the final query: " + query);
  url = FILTERS_URL.concat(query);

  createPointsLayer(url);
}

function createPointsLayer(url) {
  console.log(url);
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
            color: '#333',
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
          console.log("This key has no value in locations_dict: " + this.groupValue);
        }
      } else {
        docs_no_pleiades = this['doclist']['docs'];
        console.log("The inscriptions below have no pleiades url.")
        console.log(docs_no_pleiades);
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
            color: '#333',
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
  });
  
}

function addFacetNums(inscription, facet_nums) {
  $.each(inscription, function(key, value) {
    if ((key === 'language' || key === 'religion'|| key === 'type' 
      || key === 'physical_type' || key === 'placeMenu' || key === 'material') && value) {
      for (var i = 0; i < value.length; i++) {
        if (facet_nums[value[i]] === undefined) {
          facet_nums[value[i]] = 1;
        } else {
          facet_nums[value[i]] += 1;
        }
      }
    }
  });

  return true;
}

function updateSelectMenus(facet_nums) {
  console.log("UPDATE SELECT MENUS")
  console.log('facet nums', facet_nums)
  $('.checkbox-default').each(function(index, checkbox){
    var input = $(checkbox).children('input');
    var value = input.val();
    var name = input.attr('name');
    if ($('a[data-name=' + name).text() === 'off') {
      if (facet_nums.hasOwnProperty(value)) {
        $(this).find('span').text('('+facet_nums[value]+')');
      } else {
        $(this).find('span').text('(0)');
      }
    } else {
      if (facet_nums.hasOwnProperty(value)) {
        if (filters[name].length === 0) { //no filter for particular field
          $(this).find('span').text('('+facet_nums[value]+')');
        }
      } else {
        if (filters[name].length === 0) {
          $(this).find('span').text('(0)');
        }
      }
    }
  });

  disableEnableCheckboxes();
}

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

function changeRadius(num_in_range) {
  if (num_in_range > 0) {
    return Math.sqrt(num_in_range) + 5
  } else {
    return 0;
  }
}

function hasFilters() {
  console.log("HAS FILTERS")
  var has = true;
  for (var filter in filters) {
    if (filters.hasOwnProperty(filter) && filters[filter].length > 0) {
      addFiltersToUrl(filters, FILTERS_URL);
      return;
    }
  }

  createPointsLayer(BASE_URL);
}

$('#place-filter').change(function() {
  var selected = $('#place-filter input:checked');
  console.log(selected);
  filters['place'] = [];
  selected.each(function() {
    filters['place'].push($(this).val());
  });
  hasFilters();
});

$('#type-filter').change(function() {
  var selected = $('#type-filter input:checked');
  filters['type'] = [];
  selected.each(function() {
    filters['type'].push($(this).val());
  });
  hasFilters();
});

$('#physical_type-filter').change(function() {
  var selected = $('#physical_type-filter input:checked');
  filters['physical_type'] = [];
  selected.each(function() {
    filters['physical_type'].push($(this).val());
  });
  hasFilters();
});

$('#language-filter').change(function() {
  var selected = $('#language-filter input:checked');
  filters['language'] = [];
  selected.each(function() {
    filters['language'].push($(this).val());
  });
  hasFilters();
});

$('#religion-filter').change(function() {
  var selected = $('#religion-filter input:checked');
  filters['religion'] = [];
  selected.each(function() {
    filters['religion'].push($(this).val());
  });
  hasFilters();
});

$('#material-filter').change(function() {
  var selected = $('#material-filter input:checked');
  filters['material'] = [];
  selected.each(function() {
    filters['material'].push($(this).val());
  });
  hasFilters();
});

// OVERLAYS

var roman_provinces;
var roman_roads;
var byzantine_provinces_400CE;
var iip_regions;

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
  }
});

function highlightProvince(e) {
    var layer = e.target;
    console.log(e);
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

function onEachRomanProvince(feature, layer) {
  layer.bindTooltip('<strong>Roman Province</strong><br>' + feature.properties.province, {sticky: true, direction: 'center', offset: [0, 18], className: 'roman-province tooltip'});
  layer.on({
      mouseover: highlightProvince,
      mouseout: function() {
        layer.closeTooltip();
        roman_provinces.resetStyle(layer);
      }
  });
}

function onEachByzantine(feature, layer) {
  layer.bindTooltip('<strong>Byzantine Province</strong><br>' + feature.properties.Name, {sticky: true, direction: 'center', offset: [0, 18], className: 'byzantine-province tooltip'});
  layer.on({
      mouseover: highlightProvince,
      mouseout: function() {
        layer.closeTooltip();
        byzantine_provinces_400CE.resetStyle(layer);
      }
  });
}

function onEachIIP(feature, layer) {
  layer.bindTooltip('<strong>IIP Region</strong><br>' + feature.properties.Name, {sticky: true, direction: 'center', offset: [0, 18], className: 'iip-region tooltip'});
  layer.on({
    mouseover: highlightProvince,
    mouseout: function() {
      layer.closeTooltip();
      iip_regions.resetStyle(layer);
    }
  })
}


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


// CHECKBOX MENU OPTIONS

$('#roman_provinces').click(function() {
  if (mymap.hasLayer(roman_provinces)){
        mymap.removeLayer(roman_provinces);
    console.log("roman_empire_provinces_overlay removed");
  } else {
    mymap.addLayer(roman_provinces);
    console.log("roman_empire_provinces_overlay added");
  }
});

$('#roman_roads').click(function() {
  if (mymap.hasLayer(roman_roads)){
        mymap.removeLayer(roman_roads);
    console.log("roman_roads_overlay removed");
  } else {
    mymap.addLayer(roman_roads);
    console.log("roman_roads_overlay added");
  }
});

$('#byzantine_provinces_400CE').click(function() {
  if (mymap.hasLayer(byzantine_provinces_400CE)){
        mymap.removeLayer(byzantine_provinces_400CE);
    console.log("byzantine_provinces_400CE overlay removed");
  } else {
    mymap.addLayer(byzantine_provinces_400CE);
    console.log("byzantine_provinces_400CE overlay added");
  }
});

$('#iip_regions').click(function() {
  if (mymap.hasLayer(iip_regions)){
        mymap.removeLayer(iip_regions);
    console.log("iip_regions overlay removed");
  } else {
    mymap.addLayer(iip_regions);
    console.log("iip_regions overlay added");
  }
})


var satelite_tile = L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw', {
    attribution: 'satelite',
        maxZoom: 11,
        id: 'mapbox.satellite',
        accessToken: 'pk.eyJ1IjoiZGs1OCIsImEiOiJjajQ4aHd2MXMwaTE0MndsYzZwaG1sdmszIn0.VFRnx3NR9gUFBKBWNhhdjw'
    })


$('#overlay_satelite').click(function(){
    if (mymap.hasLayer(base_tile)){
        mymap.removeLayer(base_tile);
        satelite_tile.addTo(mymap);
        console.log("satelite view on");
    }else{
        mymap.removeLayer(satelite_tile);
        base_tile.addTo(mymap);
        console.log("satelite view off");
    }

});

function computeSliderValue(value) {
  if (value > 0) {
    return value + " CE";
  } else if (value < 0) {
    return value*(-1) + " BCE";
  } else {
    return value;
  }
}

function updateDateFieldValue(slider_value, checkbox_id) {
  if (slider_value > 0) {
    $('#' + checkbox_id + '_1').prop('checked', true);
    return slider_value;
  } else {
    $('#' + checkbox_id + '_0').prop('checked', true);
    return slider_value * (-1);
  }
}

function filterByDateRange() {
  var low = $('#slider-range').slider("option", "values")[0];
  var high = $('#slider-range').slider("option", "values")[1]
  facet_nums = {};
  var promises = [];
  points_layer.eachLayer(function(point) {
    var num_in_range = 0;
    for (var j in point['options']['inscriptions']) {
      var inscr =  point['options']['inscriptions'][j];
      if(inscr['notBefore'] == null) {
        inscr['notBefore'] = $("#slider-range").slider("option", "min")
      } 
      if (inscr['notAfter'] == null) {
        inscr['notAfter'] = $("#slider-range").slider("option", "max")
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

  Promise.all(promises)
    .then((results) => {
      updateSelectMenus(facet_nums);
    })
    .catch((e) => {
      console.log("ERROR")
      console.log(e);
    });
}

function showInscriptions(inscriptions) {
  $('#map-inscriptions-box ul').empty();
  for (inscription in inscriptions) {
    if (inscriptions.hasOwnProperty(inscription)) {
      $('#map-inscriptions-box ul').prepend('<li class="inscription" id=' + inscription + '><label>' 
        + inscription.toUpperCase().substr(0,4) + ' ' + inscription.substr(4) + '</label></li>');
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
      // $('#' + inscription).append('<br>Type: ' + inscriptions[inscription]['type'] + '<br>Physical Type: ' + inscriptions[inscription]['physical_type']
      //   + '<br>Language: ' + inscriptions[inscription]['language_display'] + '<br>Religion: ' 
      //   + inscriptions[inscription]['religion'] + '<br>Material: ' + inscriptions[inscription]['material'] + '<br>');
    }
  }
}

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


createLocationsDict();

$(".select-multiple > a").click(function() {
  var filter = $(this).data('name');
  if ($(this).text().includes("on")) {
    $(this).text("off");
    $('#'+filter+'-filter > .checkbox.checkbox-default').each(function(index, checkbox) {
      this.classList.add('checkbox-circle');
      $(this).children('input').prop('checked', false);
    });
    ops[filter] = ' AND ';
    filters[filter] = []
  } else {
    $(this).text("on");
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

$('.checkbox-default').each(function(index, checkbox) {
  var input = $(checkbox).find('input');
  $(checkbox).prepend(input);
});

$('.filter-container label').each(function(index) {
  $(this).append('<span class="facet-count"></span>');
});