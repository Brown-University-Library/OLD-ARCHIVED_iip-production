$(window).load(function() {
	langSelect($('#language').find(":selected").val())
});

function langSelect(option) {
	if(option == "Latin") {
		$("#latin-table").show()
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