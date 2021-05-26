function load_loader(e) {
	var title = $('.search-field').val();
	$("#loader").fadeIn();
	$.ajax({
		url: '/',
		type: 'POST',
		data: {
			'title': title
		},
		dataType: 'json',
		success: function () {
			$("#loader").delay(500).fadeOut();
		},
	});
}