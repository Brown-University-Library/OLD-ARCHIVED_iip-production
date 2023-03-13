(function(){

var Conv = new CETEI();

Conv.addBehaviors({'handlers':{
    'graphic': function(e) {}
}});

function shortDisplay(domTarget) {

    console.log("bd- short display: transcription trim");

    var xmlURL = $(".xml_url", domTarget).attr('href');
    console.log( "bd- shortDisplay() xmlURL try-1, ```" + xmlURL + "```" );
    var insc_url = domTarget.getElementsByTagName( 'a' )[0].href;
    // xmlURL = insc_url.replace( "viewinscr", "view_xml" ) + "/";
    xmlURL = insc_url.replace( "viewinscr", "view_xml" );
    console.log( "bd- shortDisplay() xmlURL try-02, ```" + xmlURL + "```" );

    $.get(xmlURL, function(data) {
        console.log( "bd- in get()" );
        console.log( "bd- data, ```" + data + "```" );  // xml document
        if (typeof data == 'string') {
            console.log( "bd- data is type string" );
            data = (new DOMParser()).parseFromString(data, 'application/xml');
        }
        Conv.domToHTML5(data,function(parsed, self) {
            // console.log( "bd- parsed, ```" + parsed.outerHTML + "```" );  // the xml
            var transcription = $(parsed).find("tei-div[subtype=transcription]");
            // console.log( "bd- transcription[0], ```" + transcription[0] + "```" );
            // console.log( "bd- transcription, ```" + transcription[0].outerHTML + "```" );

            var diplomatic = $(parsed).find("tei-div[subtype=diplomatic]");
            if (transcription.text().trim()) {
                console.log( "bd- transcription.text() found" );
                $(domTarget).find(".transcription").append(transcription);
                console.log( "bd- transcription html updated" );
            } else if(diplomatic.text().trim()) {
                console.log( "bd- diplomatic.text() found" );
                $(domTarget).find(".transcription .short_header").text("Diplomatic");
                $(domTarget).find(".transcription").append(diplomatic);
            } else {
                console.log( "bd- not found" );
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

    console.log("long display");


    var xmlURL = $("#viewXml a").attr('href');
    console.log( "in longDisplay(); xmlURL, ", xmlURL );
    $.get(xmlURL, function(data) {
        console.log( "data, ", data );
        if (typeof data == 'string') {
            data = (new DOMParser()).parseFromString(data, 'application/xml');
        }
        Conv.domToHTML5(data,function(parsed, self) {
            var transcription = $(parsed).find("tei-div[subtype=transcription]"); // NOTE: transcription here is not a normal js object, its a jquery or CETEI object.
            var diplomatic = $(parsed).find("tei-div[subtype=diplomatic]");
            var translation = $(parsed).find("tei-div[type=translation]");

            /* transcription display... */
            var p_el = transcription.children()[0];
            console.log( "in longDisplay(); p_el, ", p_el );
            var inside_p_length = p_el.innerHTML.trim().length;
            console.log( "in longDisplay(); inside_p_length, ", inside_p_length );
            if (inside_p_length == 0) {
                console.log( "in longDisplay(); applying no-transcription message" )
                $(domTarget).find(".transcription").html("[no transcription]");
            } else {
                console.log( "in longDisplay(); found content within p-tag, so applying that html" )
                $(domTarget).find(".transcription").html(transcription);
            }

            /* diplomatic display... */
            var p_dip_el = diplomatic.children()[0];
            console.log( "in longDisplay(); p_dip_el, ", p_dip_el );
            var inside_p_dip_length = p_dip_el.innerHTML.trim().length;
            console.log( "in longDisplay(); inside_p_dip_length, ", inside_p_dip_length );
            if (inside_p_dip_length == 0) {
                console.log( "in longDisplay(); applying no-diplomatic message" )
                $(domTarget).find(".diplomatic").html("[no diplomatic]");
            } else {
                console.log( "in longDisplay(); found content within diplomatic p-tag, so applying that html" )
                $(domTarget).find(".diplomatic").html(diplomatic);
            }
            // if(diplomatic.text().trim()) {
            //     $(domTarget).find(".diplomatic").html(diplomatic);
            // } else {
            //     $(domTarget).find(".diplomatic").html("[no diplomatic]");
            // }

            /* translation display... */
            var p_trnsltn_el = translation.children()[0];
            console.log( "in longDisplay(); p_trnsltn_el, ", p_trnsltn_el );
            var inside_p_trnsltn_length = p_trnsltn_el.innerHTML.trim().length;
            console.log( "in longDisplay(); inside_p_trnsltn_length, ", inside_p_trnsltn_length );
            if (inside_p_trnsltn_length == 0) {
                console.log( "in longDisplay(); applying no-translation message" )
                $(domTarget).find(".translation").html("[no translation]");
            } else {
                console.log( "in longDisplay(); found content within translation p-tag, so applying that html" )
                $(domTarget).find(".translation").html(translation);
            }
            // if (translation.text().trim()) {
            //     $(domTarget).find(".translation").html(translation);
            // } else {
            //     $(domTarget).find(".translation").html("[no translation]");
            // }
        });
    }, 'xml');
}

// $("#search_results tr[id]").each( function() {
//     console.log( "calling shortDisplay()" );
//     shortDisplay(this);
// });

// $(".single_inscription_stuff").each( function() {  // grrr -- that should work!!
$(".single_inscription_data_row").each( function() {
    console.log( "calling shortDisplay()" );
    shortDisplay(this);
});

$("#single_inscription .insText").each(function() {
	console.log("DEBUG", 'longDisplay', this);
	console.log("DEBUG", 'longDisplay', this);
	console.log("DEBUG", 'longDisplay', this);
	console.log("DEBUG", 'longDisplay', this);
	console.log("DEBUG", 'longDisplay', this);
    longDisplay(this);
});

})();
