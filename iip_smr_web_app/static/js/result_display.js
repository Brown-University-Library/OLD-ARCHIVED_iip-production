(function(){

var Conv = new CETEI();

Conv.addBehaviors({'handlers':{
    'graphic': function(e) {}
}});

function shortDisplay(domTarget) {
    var xmlURL = $(".xml_url", domTarget).attr('href');
    $.get(xmlURL, function(data) {
        if (typeof data == 'string') {
            data = (new DOMParser()).parseFromString(data, 'application/xml');
        }
        Conv.domToHTML5(data,function(parsed, self) {
            var transcription = $(parsed).find("tei-div[subtype=transcription]");
            var diplomatic = $(parsed).find("tei-div[subtype=diplomatic]");
            if (transcription.text().trim()) {
                $(domTarget).find(".transcription").append(transcription);
            } else if(diplomatic.text().trim()) {
                $(domTarget).find(".transcription .short_header").text("Diplomatic");
                $(domTarget).find(".transcription").append(diplomatic);
            } else {
                $(domTarget).find(".transcription").append("<tei-div>[no transcription]</tei-div>");
            }

            var translation = $(parsed).find("tei-div[type=translation]");
            if (translation.text().trim()) {
                $(domTarget).find(".translation").append(translation);
            } else {
                $(domTarget).find(".translation").append("<tei-div>[no translation]</tei-div>");
            }
        });
    }, 'xml');
}

function longDisplay(domTarget) {
    var xmlURL = $("#viewXml a").attr('href');
    $.get(xmlURL, function(data) {
        if (typeof data == 'string') {
            data = (new DOMParser()).parseFromString(data, 'application/xml');
        }
        Conv.domToHTML5(data,function(parsed, self) {
            var transcription = $(parsed).find("tei-div[subtype=transcription]");
            var diplomatic = $(parsed).find("tei-div[subtype=diplomatic]");
            var translation = $(parsed).find("tei-div[type=translation]");

            if (transcription.text().trim()) {
                $(domTarget).find(".transcription").html(transcription);
            } else {
                $(domTarget).find(".transcription").html("[no transcription]");
            }

            if(diplomatic.text().trim()) {
                $(domTarget).find(".diplomatic").html(diplomatic);
            } else {
                $(domTarget).find(".diplomatic").html("[no diplomatic]");
            }

            if (translation.text().trim()) {
                $(domTarget).find(".translation").html(translation);
            } else {
                $(domTarget).find(".translation").html("[no translation]");
            }
        });
    }, 'xml');
}

$("#search_results tr[id]").each( function() {
    shortDisplay(this);
});

$("#single_inscription .insText").each(function() {
    longDisplay(this);
});

})();
