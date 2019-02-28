
// //IIP Group
// var GROUP = "180188";

// function add_citation(ztag) {
//     var targets = $("[bibl="+ztag+"]");
//     if (ztag === "ms") {
//         targets.html("Supplied by Michael Satlow.");
//     }
//     console.log(ztag);


//     var req = new XMLHttpRequest();
//     req.open("GET", "https://api.zotero.org/groups/" + GROUP + "/items?tag=" + ztag + "&include=bib" + "&style=apa", true);
//     req.setRequestHeader("Zotero-API-Version", "3");
//     req.onload = function() {
//         var bibs = JSON.parse(this.response);
//         targets.html("");
//         if (bibs.length > 0) {
//             bibs.forEach(function(b) {
//                 console.log(Object.entries(b));
//                 targets.append(b.bib);   
//                 $(".csl-entry", targets).css('text-decoration', 'underline');
//                 $(".csl-entry", targets).css('color', 'blue');
//                 $(".csl-entry", targets).css( 'cursor', 'pointer' );
//                 $(".csl-entry", targets).on('click', function() {
//                     location.href = b.links.alternate.href;
//                         $(this).css("color", "red");

//                 });
//             });
//         } else {
//             targets.innerHTML = "Not found: " + ztag;
//         }

//         targets.each(function(i,d) {
//             d = $(d);
//             var ntype = d['context']["ntype"];
//             var n = d['context']["n"];
//             if (ntype) {
//                 if (ntype === "page") {
//                     $(".csl-entry", d).append(" <span>(p." + n + ")</span>");
//                 } else if (ntype === "insc") {
//                     $(".csl-entry", d).append("<span>(inscription " + n + ")</span>");
//                 } else {
//                     $(".csl-entry", d).append("<span>("+ntype + " " + n + ")</span>");
//                 }
//             }
//         });
//     };

//     req.onerror = function() {

//     };
//     req.send();
// }

// $(document).ready(function(){




//     console.log("ZOTERO");




//     $('.facetHeaderText').livequery(function(){
//         $(this).click(function(event){
//             $(this).toggleClass('facetMenuOpened');
//             $(this).next('ul').toggle('30');
//             });
//     });

//     $('#narrow_results a.showHideFacets').livequery(function(){
//         $(this).click(function(event){
//          event.preventDefault();
//         $('.facetHeaderText').each(function(){
//             $(this).toggleClass('facetMenuOpened');
//             $(this).next('ul').toggle('30');
//             });
//         });            
//     });


//     $('.facetLink').livequery(function(){
//         $(this).click(function(event){
//                 event.preventDefault();
//                 var isDisplayStatus = /display_status:.*/;
//                 //split the qstring into clauses
//                 var split_qstring = qstring.split(/\s+(?:AND|OR)\s+/);
//                 var newQStringParts = [];

//                 for (var i = 0; i < split_qstring.length; i++) {
//                     if (!isDisplayStatus.test(split_qstring[i])) {
//                         newQStringParts.push(split_qstring[i]);
//                     }
//                 }
//                 newQStringParts.push($(this).attr('href') +':"'+$(this).attr('id') + '"');

//                 //Load the new results page
//                 window.location.search = "?q="+newQStringParts.join(" AND ") + "&resultsPage=1";
//         });
//     });
// });


//Collection U2J49649 is also called IIP
var collection = "U2J49649";
//IIP Group
var GROUP = "180188";

function retrieve_bib(id_list, callback) {
  var tags = id_list.join(" || ");
  console.log(tags);
  var req = new XMLHttpRequest();
  req.open("GET", "https://api.zotero.org/groups/" + GROUP + "/items?tag=" + tags + "&content=bib,json" + "&style=apa", true);
  req.setRequestHeader("Zotero-API-Version", "3");
  req.onload = callback;
  req.send();
}

var bibliographies = {};

function render_bibliography() {
  var bib_entries = $("span.z_id");
  var iip_id_list = [];
  for (var i = 0; i < bib_entries.length; i++) {
    var b = bib_entries[i].textContent.split("|");
    var new_id = b[0].trim();
    if (iip_id_list.indexOf(new_id) == -1) {
      iip_id_list.push(new_id);
    }
    console.log('DEBUG:\tiip_id_list', iip_id_list);
  }

  retrieve_bib(iip_id_list, function () {
    if (this.status == 200) {

      var responseXML = this.responseXML;
      console.log("DEBUG:\tresponseXML", responseXML);
      var entrie_list = responseXML.documentElement.getElementsByTagName('entry');
      console.log("DEBUG:\tentries", entrie_list);
      let list_content = { 'bibl': [], 'url': [], 'json': [] };

      for (var i = 0; i < entrie_list.length; i++) {
        var contents;
        var contents_f = entrie_list[i].getElementsByTagName("content")[0]; // bib
        console.log('DEBUG\tcontents_f', contents_f);
        if (contents_f.children) {
          contents = contents_f.children;
        } else {
          contents = contents_f.getElementsByTagName("subcontent");
        }
        var entryjson = JSON.parse(contents[1].textContent);
        console.log("entryjson", entryjson);
        console.log("DEBUG:\tentryjson.archiveLocation", entryjson.archiveLocation);
        console.log('DEBUG:\tentryjson.key', entryjson.key);

        bibliographies[entryjson.archiveLocation] = {};
        bibliographies[entryjson.archiveLocation].parsed = entryjson;
        bibliographies[entryjson.archiveLocation].url = entrie_list[i].getElementsByTagName("id")[0].textContent;

        list_content['json'].push(entryjson);
        list_content['url'].push(entrie_list[i].getElementsByTagName("id")[0].textContent);
        list_content['bibl'].push(contents_f.getElementsByClassName('csl-bib-body')[0].innerHTML);
      }
      console.log("bibliographies", bibliographies);
      /************************************/
      // this is for bibls
      $("ul.biblToRetrieve").each(function () {
        console.log('Activated!');

        var bspan = $(this).find('span')[0];
        b = bspan.innerHTML.trim();
        console.log("DEBUG:\tb\t\t\t\t\t", b);
        var pages = $(this).find('ul li');
        var new_html;
        let reference = '';

        this.attributes.class.value = ""; 
        if (pages.length !== 0) {
          reference += "(";
        }
        var semicolon = "; ";
        for (var i = 0; i < pages.length; i++) {
          if (i == pages.length - 1) {
            semicolon = "";
          }
          console.log("DEBUG:\tpages[i]", pages[i]);
          var entry = pages[i].innerHTML.split("|");
          entry = entry[0].replace(/\s+/g, '').split('.');
          console.log("DEBUG:\tentry", entry);
          if (entry[0] == 'page' || entry[0] == 'p') {
            reference += "Page. " + entry[1] + semicolon;
          } else {
            if (entry.length === 1)
              reference += "Insc." + entry[0] + semicolon;
            else {
              reference += "Insc." + entry[1] + semicolon;
            }
            console.log('DEBUG:\tnew_html', reference);
          }
        }
        if (pages.length != + 0) {
          reference += ")<br/>";
        }

        $(this).find("ul")[0].innerHTML = "";

        try {
          innerHTML_list = []
          for (let i = 0; i < list_content['bibl'].length; i++) {
            let link = "<a style='display:inline;' href='" + list_content['url'][i] + "'>(Link to Full Entry)</a>";

            innerHTML_list.push('<div>' +
              list_content['bibl'][i] + reference + link
              + "</div>"
            );
          }
          new_html = innerHTML_list.join('<br></br>');
          console.log("DEBUG:\tnewhtml", new_html);
          bspan.innerHTML = new_html;
        } catch (err) {
          console.log(err);
          console.log('WARNING:\tCatch error here 1!')
          new_html = b + " (Citation not found in Zotero!)";
          bspan.innerHTML = new_html;
          pages.each(function () {
            var entry = $(this).text().split("|");
            if (entry[0] == "page") {
              $(this).text("Page " + entry[1]);
            } else {
              $(this).text("Inscription " + entry[1]);
            }
          });
          return;
        }
      });
      /************************************/

      // this is for upper threee parts
      $("span.biblToRetrieve").each(function () {
        /* cleaning the arguments */
        var b = this.innerHTML.split("|");
        console.log('DEBUG:\t b in biblToRetrieve');
        console.log(b);
        b_array = Array()
        split_substring = "', '"
        idx_firstsplit = b[0].indexOf(split_substring)
        idx_secondsplit = b[0].indexOf(split_substring, idx_firstsplit + 1)
        idx_endsplit = b[0].indexOf("')");
        b_array[0] = b[0].slice(2, idx_firstsplit);
        b_array[1] = b[0].slice(idx_firstsplit + split_substring.length, idx_secondsplit);
        b_array[2] = b[0].slice(idx_secondsplit + split_substring.length, idx_endsplit);
        console.log('HaDEBUG:\t b_array ');
        console.log(b_array);
        /* cleaning the arguments finished! */

        try {

          let colon = ": ";
          if (b_array[2] === "")
            colon = "";
          innerHTML_list = []
          for (let i = 0; i < list_content['bibl'].length; i++) {
            innerHTML_list.push('<div>' +
              list_content['bibl'][i] + '(' + b_array[1] + '.' + b_array[2] + ')' + " (<a href='" + list_content['url'][i] + "'>Full Entry</a>)"
              + "</div>"
            );
          }
          this.innerHTML = innerHTML_list.join('');
        }

        catch (err) {
          console.log('Catch error here 2!');
          console.log(b_array);
          if (b_array[0] == "ms") {
            this.innerHTML = "Supplied by Michael Satlow";
          } else {
            var txt = b_array[0] + " ";
            if (b_array[1] == 'page') {
              txt += "Page " + b_array[2];
            } else {
              txt += "Inscription " + b_array[2];
            }
            this.innerHTML = txt + " (Citation Not Found)";
            console.log("DEBUG:\tthis.innerHTML", this.innerHTML);
          }
        }

        this.attributes.class.value = "";
      });
    }
  });
}

$(document).ready(function () {
  $('.facetHeaderText').livequery(function () {
    $(this).click(function (event) {
      $(this).toggleClass('facetMenuOpened');
      $(this).next('ul').toggle('30');
    });
  });

  $('#narrow_results a.showHideFacets').livequery(function () {
    $(this).click(function (event) {
      event.preventDefault();
      $('.facetHeaderText').each(function () {
        $(this).toggleClass('facetMenuOpened');
        $(this).next('ul').toggle('30');
      });
    });
  });


  $('.facetLink').livequery(function () {
    $(this).click(function (event) {
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
      newQStringParts.push($(this).attr('href') + ':"' + $(this).attr('id') + '"');

      //Load the new results page
      window.location.search = "?q=" + newQStringParts.join(" AND ") + "&resultsPage=1";
    });
  });
});

