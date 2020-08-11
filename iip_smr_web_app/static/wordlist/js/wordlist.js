var bolded = false

$(window).load(function() {
	langSelect($('#language').find(":selected").val())
	addAtoZLinks()
});

function boldKWIC() {
	var table = document.getElementById("latin-pos-table");
	var curword = ""
	for (var i = 0, row; row = table.rows[i]; i++) {
		if($(row).attr('class').includes("level1")) {
			for(var j = 0, col; col = row.cells[j]; j++) {
				var cvar = $(col)
				if(cvar.attr('class').includes("kwic")) {
					const rv = cvar.html().split(" " + curword + " ", 2)
					cvar.html(rv[0] + " <strong>" + curword + "</strong> " + rv[1])
				} else {
					const rowval = cvar.html()
					curword = rowval.substr(0, rowval.indexOf(' '));
				}
			}
		}
	}
}

function addAtoZLinks() {
	var links = $(".alphalink")
	var i
	for(i = 0; i < links.length; i++) {
		var link = $(links[i])
		link.click(function(event) {
			const letter = $(event.target).html()
			findAndScroll(letter)
		})
	}
}

function findAndScroll(letter) {
	var table = document.getElementById("latin-pos-table");
	for (var r = 0, row; row = table.rows[r]; r++) {
		if($(row).attr('class').includes("level0") && 
			$(row).find("b").html()[0] == letter) {
			offset = row.getBoundingClientRect().top - 80;
			window.scrollTo({
				top: offset
			});
			return;
		}
	}
}

function posFilter() {
	checked = new Set()
	$(".pos-filter").each(function(i, obj) {
		if(obj.checked) {
			checked.add(obj.value)
		}
	})
	const noCheck = checked.size == 0
	var table = document.getElementById("latin-pos-table")
	var hiding = false
	for(var r = 0, row; row = table.rows[r]; r++) {
		if($(row).attr('class').includes("level0")) {
			const rowHTML = row.innerHTML
			const ind = rowHTML.indexOf("</b>")
			const pos = rowHTML.substring(ind + 5, rowHTML.indexOf(" ", ind + 6))
			if(noCheck || checked.has(pos)) {
				$(row).show()
				hiding = false
			} else {
				$(row).hide()
				hiding = true
			}
		} else if (hiding) {
			$(row).hide()
		}
	}
}


function langSelect(option) {
	if(option == "Latinnew" || option == "Latinold") {
		data = requestLang(option)
		$("#latin-table").html(data)
		$("#latin-table").show()
		boldKWIC()
		$("#in-progress").hide()
	}else if (option == "Greek" || option == "Hebrew"){
		$("#latin-table").hide()
		$("#in-progress").show()
	} else {
		$("#latin-table").hide()
		$("#in-progress").hide()
	}
}

function requestLang(lang) {

	requrl = "/wordlist/"
	retdata = null

	if(lang == "Latinold") {
		requrl += "old_latin_data"
	} else if (lang == "Latinnew") {
		requrl += "new_latin_data"
	}

	$.ajax({
		url: requrl,
		type: 'get',
		async: false,
		success: function(data) {
			retdata = data
		},
		failure: function(data) {
			console.log("failure")
			retdata = null
		}
	});
	return retdata
}

function collapseToggle(obj) {
	var button = $(obj)
	const togclass = "." + button.attr('id').substring(3)
	if(button.html() == "+") {
		button.html("-")
		$(togclass).show()
	} else {
		button.html("+")
		$(togclass).hide()
	}
}