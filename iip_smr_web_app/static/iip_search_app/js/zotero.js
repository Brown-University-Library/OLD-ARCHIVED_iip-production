
//IIP Group
var GROUP = "180188";

id_dict = {
    0:'diplomatic',
    1:'transcription',
    2:'translation',
    3:'bibllist',
}
total_links_array = {};
async function add_citation(ztag) {
    //assign targets html
    var targets_html = $("[bibl="+ztag+"]");
    //ztag is inscription ID
    console.log(ztag);
    console.log(targets_html);
    if (ztag === "ms") {
        targets_html.html("Supplied by Michael Satlow.");
    }
    console.log(ztag);

    let links_array = new Array();
    var req = new XMLHttpRequest();
    req.open("GET", "https://api.zotero.org/groups/" + GROUP + "/items?tag=" + ztag + "&include=bib" + "&style=apa", true);
    console.log("https://api.zotero.org/groups/" + GROUP + "/items?tag=" + ztag + "&include=bib" + "&style=apa", true);
    req.setRequestHeader("Zotero-API-Version", "3");
    req.onload = function() {
        //bibs response from api call
        var bibs = JSON.parse(this.response);
        console.log(bibs);
        targets_html.html("");
        if (bibs.length > 0) {
            bibs.forEach(function(b) {
                console.log('DEBUG: foreach ------- b', b);
                console.log('current ztag', ztag);
                console.log(b.bib);
                let href = b.links.alternate.href;
                links_array.push(href);
                total_links_array[ztag] = href;
                console.log("DEBUG:b.bib", typeof(targets_html));
                targets_html.append(b.bib);
                // $(".csl-entry", targets_html).css( 'cursor', 'pointer' );
                // $(".csl-entry", targets_html).on('click', function() {
                //     location.href = href;
                //         $(this).css("color", "red");
                // });
            });
        } else {
            targets_html.innerHTML = "Not found: " + ztag;
        }

        console.log(targets_html);
        //iterating over each html node child
        //index, specific node
        targets_html.each(function(i,d) {
            console.log('DEBUG: i', i);
            console.log('DEBUG: d', d);
            d = $(d);
            console.log('DEBUG: d', d);
            var ntype = d.attr('ntype');
            var n = d.attr('n');
            console.log("DEBUG: *********** ntype", ntype)
            console.log("DEBUG: *********** n", n)



            if (ntype) {
                if (ntype === "page") {
                    $(".csl-entry", d).append("<div style='display:inline; margin-left:.5em;'><span>(page." + n + ")</span></div>");
                } else if (ntype === "insc") {
                    $(".csl-entry", d).append("<div style='display:inline; margin-left:.5em;'><span>(inscription. " + n + ")</span></div>");
                } else {
                    $(".csl-entry", d).append("<div style='display:inline; margin-left:.5em;'><span>("+ntype + " " + n + ")</span></div>");
                }
            };

            id = id_dict[i];
            if (i <= 2) {
                select_exp = '#' + id + ' .csl-bib-body';
                d_html = $(select_exp);
                for (let [i, link_href] of links_array.entries()) {
                    //error here
                    //console.log(d_html[i].childNodes);
                    //$(d_html[i] + "> div.csl-entry > i:nth-child(1)").css("display","none");
                    //$(d_html[i]).append("<div style='float:right;'><a href='"+link_href+"' target='_blank'>(See bin Zotero)</a><div>");
                }
            }
        });
    };
    req.onerror = function() {
    };
    req.send();
}

function add_cita_bibl() {
    id = id_dict[3]; // bibllist
    select_exp = '#' + id + ' .biblToRetrieve';
    d_html = $(select_exp);
    console.log(d_html);
    let final_parts_html = new Array();
    for (let i = 0; i <= d_html.length; i ++) {
        let currrent_find = $(d_html[i]).find('.csl-bib-body');
        console.log('currrent_find', currrent_find);
        final_parts_html = final_parts_html.concat(currrent_find);
    }
    console.log('final_parts_html', final_parts_html);
    console.log('total_links_array', typeof(total_links_array));

    for (let i_link = 0; i_link < Object.entries(total_links_array).length; i_link++) {
        parent_div_ztag = $(final_parts_html[i_link]).parent().attr('bibl')
        link_href = total_links_array[parent_div_ztag];
        console.log('inner for loop', link_href);
        $(final_parts_html[i_link]).append("<div style='float:right;'><a href='"+link_href+"' target='_blank'>(See in Zotero)</a><div>");
    }
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
                console.log( "in facetLink-livequery; isDisplayStatus, ", isDisplayStatus );

                console.log( "qstring, ", qstring );

                //split the qstring into clauses
                var split_qstring = qstring.split(/\s+(?:AND|OR)\s+/);
                console.log( "in facetLink-livequery; split_qstring, ", split_qstring );
                console.log( "split_qstring as stringified object, ", JSON.stringify(split_qstring) );

                var newQStringParts = [];

                for (var i = 0; i < split_qstring.length; i++) {
                    if (!isDisplayStatus.test(split_qstring[i])) {
                        newQStringParts.push(split_qstring[i]);
                    }
                }
                newQStringParts.push($(this).attr('href') +':"'+$(this).attr('id') + '"');

                var q_url = "?q="+newQStringParts.join(" AND ") + "&resultsPage=1";
                console.log( "in facetLink-livequery; q_url, ", q_url );

                //Load the new results page
                // window.location.search = "?q="+newQStringParts.join(" AND ") + "&resultsPage=1";
                window.location.search = q_url;
        });
    });
});

// //Collection U2J49649 is also called IIP
// var collection = "U2J49649";
// //IIP Group
// var GROUP = "180188";

// function retrieve_bib(id_list, callback) {
//   var tags = id_list.join(" || ");
//   console.log(tags);
//   var req = new XMLHttpRequest();
//   req.open("GET", "https://api.zotero.org/groups/" + GROUP + "/items?tag=" + tags + "&content=bib,json" + "&style=apa", true);
//   req.setRequestHeader("Zotero-API-Version", "3");
//   req.onload = callback;
//   req.send();
// }

// var bibliographies = {};

// function render_bibliography() {
//   var bib_entries = $("span.z_id");
//   var iip_id_list = [];
//   for (var i = 0; i < bib_entries.length; i++) {
//     var b = bib_entries[i].textContent.split("|");
//     var new_id = b[0].trim();
//     if (iip_id_list.indexOf(new_id) == -1) {
//       iip_id_list.push(new_id);
//     }
//     console.log('DEBUG:\tiip_id_list', iip_id_list);
//   }

//   retrieve_bib(iip_id_list, function () {
//     if (this.status == 200) {

//       var responseXML = this.responseXML;
//       console.log("DEBUG:\tresponseXML", responseXML);
//       var entrie_list = responseXML.documentElement.getElementsByTagName('entry');
//       console.log("DEBUG:\tentries", entrie_list);
//       let list_content = { 'bibl': [], 'url': [], 'json': [] };

//       for (var i = 0; i < entrie_list.length; i++) {
//         var contents;
//         var contents_f = entrie_list[i].getElementsByTagName("content")[0]; // bib
//         console.log('DEBUG\tcontents_f', contents_f);
//         if (contents_f.children) {
//           contents = contents_f.children;
//         } else {
//           contents = contents_f.getElementsByTagName("subcontent");
//         }
//         var entryjson = JSON.parse(contents[1].textContent);
//         console.log("entryjson", entryjson);
//         console.log("DEBUG:\tentryjson.archiveLocation", entryjson.archiveLocation);
//         console.log('DEBUG:\tentryjson.key', entryjson.key);

//         bibliographies[entryjson.archiveLocation] = {};
//         bibliographies[entryjson.archiveLocation].parsed = entryjson;
//         bibliographies[entryjson.archiveLocation].url = entrie_list[i].getElementsByTagName("id")[0].textContent;

//         list_content['json'].push(entryjson);
//         list_content['url'].push(entrie_list[i].getElementsByTagName("id")[0].textContent);

//         // console.log("DEBUG:list_content['bibl']", typeof( contents_f.getElementsByClassName('csl-bib-body')[0].innerHTML) );
//         bibl_entry = contents_f.getElementsByClassName('csl-bib-body')[0];
//         list_content['bibl'].push(bibl_entry.outerHTML);
//       }
//       console.log('DEBUG@yang:list_content', list_content);
//       list_content_copy = Object.assign({}, list_content);
//       console.log("bibliographies", bibliographies);
//       /************************************/
//       // this is for bibls
//       $("div.biblToRetrieve").each(function () {
//         console.log('Activated!', this);

//         var bspan = $(this).find('ul')[0];
//         b = bspan.innerHTML.trim();
//         console.log("DEBUG:\tb\t\t\t\t\t", b);
//         var pages = $(this).find('ul li');
//         var new_html;
//         let reference = '';

//         this.attributes.class.value = "";
//         if (pages.length !== 0) {
//           reference += "(";
//         }
//         var semicolon = "; ";
//         for (var i = 0; i < pages.length; i++) {
//           if (i == pages.length - 1) {
//             semicolon = "";
//           }
//           console.log("DEBUG:\tpages[i]", pages[i]);
//           var entry = pages[i].innerHTML.split("|");
//           entry = entry[0].replace(/\s+/g, '').split('.');
//           console.log("DEBUG:\tentry", entry);
//           if (entry[0] == 'page' || entry[0] == 'p') {
//             reference += "Page. " + entry[1] + semicolon;
//           } else {
//             if (entry.length === 1)
//               reference += "Insc." + entry[0] + semicolon;
//             else {
//               reference += "Insc." + entry[1] + semicolon;
//             }
//             console.log('DEBUG:\tnew_html', reference);
//           }
//         }
//         if (pages.length != + 0) {
//           reference += ")<br/>";
//         }

//         $(this).find("ul")[0].innerHTML = "";

//         try {
//           console.log("DEBUG:list_content['bibl']", list_content['bibl']);
//           innerHTML_list = []
//           // for (let i = 0; i < list_content['bibl'].length; i++) {
//           list_content_i = list_content['bibl'].pop();
//           let link = "<a style='display:inline;' href='" + list_content['url'].pop() + "'>(Link to Full Entry)</a>";

//           innerHTML_list.push('<div>' +
//           list_content_i + reference + link
//             + "</div>"
//           );
//           // }
//           new_html = innerHTML_list.join('');
//           console.log("DEBUG:\tnewhtml", new_html);
//           bspan.innerHTML = new_html;
//         } catch (err) {
//           console.log(err);
//           console.log('WARNING:\tCatch error here 1!')
//           new_html = b + " (Citation not found in Zotero!)";
//           bspan.innerHTML = new_html;
//           pages.each(function () {
//             var entry = $(this).text().split("|");
//             if (entry[0] == "page") {
//               $(this).text("Page " + entry[1]);
//             } else {
//               $(this).text("Inscription " + entry[1]);
//             }
//           });
//           return;
//         }
//       });
//       /************************************/
//       list_content = list_content_copy;
//       // this is for upper threee parts
//       $("span.biblToRetrieve").each(function () {
//         /* cleaning the arguments */
//         var b = this.innerHTML.split("|");
//         console.log('DEBUG:\t b in biblToRetrieve');
//         console.log(b);
//         b_array = Array()
//         split_substring = "', '"
//         idx_firstsplit = b[0].indexOf(split_substring)
//         idx_secondsplit = b[0].indexOf(split_substring, idx_firstsplit + 1)
//         idx_endsplit = b[0].indexOf("')");
//         b_array[0] = b[0].slice(2, idx_firstsplit);
//         b_array[1] = b[0].slice(idx_firstsplit + split_substring.length, idx_secondsplit);
//         b_array[2] = b[0].slice(idx_secondsplit + split_substring.length, idx_endsplit);
//         console.log('HaDEBUG:\t b_array ');
//         console.log(b_array);
//         /* cleaning the arguments finished! */

//         try {

//           let colon = ": ";
//           if (b_array[2] === "")
//             colon = "";
//           innerHTML_list = []
//           for (let i = 0; i < list_content['bibl'].length; i++) {
//             innerHTML_list.push('<div>' +
//               list_content['bibl'][i] + '(' + b_array[1] + '.' + b_array[2] + ')' + " (<a href='" + list_content['url'][i] + "'>Full Entry</a>)"
//               + "</div>"
//             );
//           }
//           this.innerHTML = innerHTML_list.join('');
//         }

//         catch (err) {
//           console.log('Catch error here 2!');
//           console.log(b_array);
//           if (b_array[0] == "ms") {
//             this.innerHTML = "Supplied by Michael Satlow";
//           } else {
//             var txt = b_array[0] + " ";
//             if (b_array[1] == 'page') {
//               txt += "Page " + b_array[2];
//             } else {
//               txt += "Inscription " + b_array[2];
//             }
//             this.innerHTML = txt + " (Citation Not Found)";
//             console.log("DEBUG:\tthis.innerHTML", this.innerHTML);
//           }
//         }

//         this.attributes.class.value = "";
//       });
//     }
//   });
// }

// $(document).ready(function () {
//   $('.facetHeaderText').livequery(function () {
//     $(this).click(function (event) {
//       $(this).toggleClass('facetMenuOpened');
//       $(this).next('ul').toggle('30');
//     });
//   });

//   $('#narrow_results a.showHideFacets').livequery(function () {
//     $(this).click(function (event) {
//       event.preventDefault();
//       $('.facetHeaderText').each(function () {
//         $(this).toggleClass('facetMenuOpened');
//         $(this).next('ul').toggle('30');
//       });
//     });
//   });


//   $('.facetLink').livequery(function () {
//     $(this).click(function (event) {
//       event.preventDefault();
//       var isDisplayStatus = /display_status:.*/;
//       //split the qstring into clauses
//       var split_qstring = qstring.split(/\s+(?:AND|OR)\s+/);
//       var newQStringParts = [];

//       for (var i = 0; i < split_qstring.length; i++) {
//         if (!isDisplayStatus.test(split_qstring[i])) {
//           newQStringParts.push(split_qstring[i]);
//         }
//       }
//       newQStringParts.push($(this).attr('href') + ':"' + $(this).attr('id') + '"');

//       //Load the new results page
//       window.location.search = "?q=" + newQStringParts.join(" AND ") + "&resultsPage=1";
//     });
//   });
// });

