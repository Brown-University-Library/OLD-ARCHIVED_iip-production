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
					const rv = cvar.html().split(curword, 2)
					cvar.html(rv[0] + "<strong>" + curword + "</strong>" + rv[1])
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


function langSelect(option) {
	if(option == "Latin") {
		$("#latin-table").show()
		if(!bolded) {
			boldKWIC()
			bolded = true
		}
		$("#in-progress").hide()
	} else if (option == "Greek" || option == "Hebrew"){
		$("#latin-table").hide()
		$("#in-progress").show()
	} else {
		$("#latin-table").hide()
		$("#in-progress").hide()
	}
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