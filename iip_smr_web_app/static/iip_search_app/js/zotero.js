
//IIP Group
var GROUP = "180188";

function add_citation(ztag) {
    var targets = $("[bibl="+ztag+"]");
    if (ztag === "ms") {
        targets.html("Supplied by Michael Satlow.");
    }
    console.log(ztag);


    var req = new XMLHttpRequest();
    req.open("GET", "https://api.zotero.org/groups/" + GROUP + "/items?tag=" + ztag + "&include=bib" + "&style=apa", true);
    req.setRequestHeader("Zotero-API-Version", "3");
    req.onload = function() {
        var bibs = JSON.parse(this.response);
        targets.html("");
        if (bibs.length > 0) {
            bibs.forEach(function(b) {
                console.log(Object.entries(b));
                targets.append(b.bib);   
                $(".csl-entry", targets).css('text-decoration', 'underline');
                $(".csl-entry", targets).css('color', 'blue');
                $(".csl-entry", targets).css( 'cursor', 'pointer' );
                $(".csl-entry", targets).on('click', function() {
                    location.href = b.links.alternate.href;
                        $(this).css("color", "red");
 
                });
            });
        } else {
            targets.innerHTML = "Not found: " + ztag;
        }

        targets.each(function(i,d) {
            d = $(d);
            var ntype = d['context']["ntype"];
            var n = d['context']["n"];
            if (ntype) {
                if (ntype === "page") {
                    $(".csl-entry", d).append(" <span>(p." + n + ")</span>");
                } else if (ntype === "insc") {
                    $(".csl-entry", d).append("<span>(inscription " + n + ")</span>");
                } else {
                    $(".csl-entry", d).append("<span>("+ntype + " " + n + ")</span>");
                }
            }
        });
    };

    req.onerror = function() {

    };
    req.send();
}

$(document).ready(function(){
    



    console.log("ZOTERO");




    $('.facetHeaderText').livequery(function(){
        $(this).click(function(event){
            $(this).toggleClass('facetMenuOpened');
            $(this).next('ul').toggle('30');
            });
    });

    $('#narrow_results a.showHideFacets').livequery(function(){
        $(this).click(function(event){
         event.preventDefault();
        $('.facetHeaderText').each(function(){
            $(this).toggleClass('facetMenuOpened');
            $(this).next('ul').toggle('30');
            });
        });            
    });


    $('.facetLink').livequery(function(){
        $(this).click(function(event){
                event.preventDefault();
                var isDisplayStatus = /display_status:.*/;
                //split the qstring into clauses
                var split_qstring = qstring.split(/\s+(?:AND|OR)\s+/);
                var newQStringParts = [];

                for (var i = 0; i < split_qstring.length; i++) {
                    if (!isDisplayStatus.test(split_qstring[i])) {
                        newQStringParts.push(split_qstring[i]);
                    }
                }
                newQStringParts.push($(this).attr('href') +':"'+$(this).attr('id') + '"');
                
                //Load the new results page
                window.location.search = "?q="+newQStringParts.join(" AND ") + "&resultsPage=1";
        });
    });
});

