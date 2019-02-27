
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
  var id_list = [];
  for (var i = 0; i < bib_entries.length; i++) {
    var b = bib_entries[i].textContent.split("|");
    var new_id = b[0].trim();
    if (id_list.indexOf(new_id) == -1) {
      id_list.push(new_id);
    }
  }

  retrieve_bib(id_list, function () {
    if (this.status == 200) {
      var responseXML = this.responseXML;
      console.log("DEBUG:\tresponseXML", responseXML);
      var entries = responseXML.documentElement.getElementsByTagName('entry');
      console.log("DEBUG:\tentries[0]", entries[0]);

      for (var i = 0; i < entries.length; i++) {
        var contents;
        var contents_f = entries[i].getElementsByTagName("content")[0]; // bib
        console.log('DEBUG\tcontents_f', contents_f);
        if (contents_f.children) {
          contents = contents_f.children;
        } else {
          contents = contents_f.getElementsByTagName("subcontent");
        }
        var entryjson = JSON.parse(contents[1].textContent);
        console.log("contents[0]", contents[0]);
        console.log("DEBUG:\tentryjson.archiveLocation", entryjson.archiveLocation);
        bibliographies[entryjson.archiveLocation] = {};
        bibliographies[entryjson.archiveLocation].parsed = entryjson;
        bibliographies[entryjson.archiveLocation].full = contents[0].textContent;
        bibliographies[entryjson.archiveLocation].url = entries[i].getElementsByTagName("id")[0].textContent;
        bibliographies[entryjson.archiveLocation].content = contents_f.getElementsByClassName('csl-bib-body')[0].innerHTML;
        console.log("DEBUG:\t", bibliographies[entryjson.archiveLocation].content);

      }

      // this is for bibls
      $("li.biblToRetrieve").each(function () {

        var bspan = $(this).find('span')[0];
        b = bspan.innerHTML.trim();
        console.log("DEBUG:\tb", b);
        var pages = $(this).find('ul li');
        var new_html;

        try {
          new_html = bibliographies[b].content;
          console.log("DEBUG:\tnewhtml", new_html);

        }
        catch (err) {
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

        this.attributes.class.value = "";
        if (pages.length !== 0) new_html += "(";
        var semicolon = "; ";
        console.log("DEBUG:\tnewhtml", new_html);
        for (var i = 0; i < pages.length; i++) {
          if (i == pages.length - 1) {
            semicolon = "";
          }
          console.log("DEBUG:\tpages[i]", pages[i]);
          var entry = pages[i].innerHTML.split("|");
          entry = entry[0].replace(/\s+/g, '').split('.');
          console.log("DEBUG:\tentry",entry);
          if (entry[0] == 'page' || entry[0] == 'p') {
            new_html += "Page. " + entry[1] + semicolon;
          } else {
            if (entry.length === 1 ) 
              new_html += "Insc." + entry[0] + semicolon;
            else {
              new_html += "Insc." + entry[1] + semicolon;
            }
            console.log('DEBUG:\tnew_html', new_html);
          }
        }
        if (pages.length != + 0) {
          new_html += ")<br/>";
        }
        console.log("DEBUG:\t", $(this).find("ul")[0]);
        $(this).find("ul")[0].innerHTML = "";
        if (bibliographies[b].url) 
          new_html += "<a style='display:inline;' href='" + bibliographies[b].url + "'>(Link to Full Entry)</a>";

        bspan.innerHTML = new_html;
        console.log('DEBUG:\tbspan.innerHTML', bspan.innerHTML);

      });

      // this is for upper threee parts
      $("span.biblToRetrieve").each(function () {
        var b = this.innerHTML.split("|");
        console.log('DEBUG:\t b');
        console.log(b);
        b_array = Array()
        split_substring = "', '"
        idx_firstsplit = b[0].indexOf(split_substring)
        idx_secondsplit = b[0].indexOf(split_substring, idx_firstsplit+1)
        idx_endsplit = b[0].indexOf("')");
        b_array[0] =  b[0].slice(2, idx_firstsplit);
        b_array[1] =  b[0].slice(idx_firstsplit + split_substring.length, idx_secondsplit);
        b_array[2] =  b[0].slice(idx_secondsplit + split_substring.length, idx_endsplit);
        console.log('HaDEBUG:\t b_array ');
        console.log(b_array);
        b = b_array;
        try {
          var entry = bibliographies[b[0]].parsed;
          var colon = ": ";
          if (b[2] === "") colon = "";
          // this.innerHTML = "<div>" +
          // entry.creators[0].lastName + ". " + "<i>" + entry.title + "</i>" + ", " + entry.date + colon + '(' + b[1] + '.' +  b[2] + ')' + " (<a href='" + bibliographies[b[0]].url + "'>Full</a>)"
          // +"</div>";
          this.innerHTML = "<div>" +
          entry.creators[0].lastName + ". " + "<i>" + entry.title + "</i>" + ", " + entry.date + colon + '(' + b[1] + '.' +  b[2] + ')' + " (<a href='" + bibliographies[b[0]].url + "'>Full</a>)"
          +"</div>";
        }
        catch (err) {
          console.log('Catch error here 2!');
          console.log(b);
          if (b[0] == "ms") {
            this.innerHTML = "Supplied by Michael Satlow";
          } else {
            var txt = b[0] + " ";
            if (b[1] == 'page') {
              txt += "Page " + b[2];
            } else {
              txt += "Inscription " + b[2];
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

