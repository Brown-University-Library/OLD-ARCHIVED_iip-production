$(document).ready(function() {

	$('body').css('display', 'none');

	$('body').fadeIn(2000);

	$('.link').click(function() {
		event.preventDefault();
		newLocation = this.href;
		$('body').fadeOut(1000, newpage);
	});

	function newpage() {
		console.log(newLocation);
		window.location = newLocation;
	}

});