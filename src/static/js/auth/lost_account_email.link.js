$(document).ready(() => {
	
	// get csrftoken
	function getCookie(name) {
	    var cookieValue = null;
	    if (document.cookie && document.cookie !== '') {
	        var cookies = document.cookie.split(';');
	        for (var i = 0; i < cookies.length; i++) {
	            var cookie = jQuery.trim(cookies[i]);
	            // Does this cookie string begin with the name we want?
	            if (cookie.substring(0, name.length + 1) === (name + '=')) {
	                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                break;
	            }
	        }
	    }
	    return cookieValue;
	}
	var csrftoken = getCookie('csrftoken');

	// js for verification code sending
	$('#email-verification-send-form').on('submit', function(event, doDefault) {
		event.preventDefault();
		$(event.currentTarget).children().removeClass("is-invalid");
		$(".invalid-feedback").remove();
		$.ajax({
			type: "POST",
			url: emailPasswordResetAPI,
			data: {'email': $(".email-verification-send-email-field").val(), 
				   'csrfmiddlewaretoken': csrfToken,
				   'check_email_exists': true
				},
			dataType: 'json',
			success: function (data, textStatus) {
				if (data.email_sent == false) {
					let responseData = $.parseJSON(data.errors);
					for (name in responseData) {
						for (var i in responseData[name]) {
							$("input[name='" + name + "']").addClass("is-invalid");
							$(`<div class="invalid-feedback">` + responseData[name][i].message + `</div>`).insertAfter("input[name='" + name + "']");
						}
					}
				} else {
					// Do nothing if succeeds, since response will be a 302 which will be catched in the error option
				}
			},
			error: function( jqXhr, textStatus, errorThrown ) {
				if (jqXhr.status == 302) {
					window.location.replace(jqXhr.responseJSON.redirect);
				} else {
					//  if is not redirect something bad happened
					$('.email-verification-send-email-field').addClass("is-invalid");
					$('#email-verification-send-form-group-div').append(`<div class="invalid-feedback">Something wrong happened. Try Again</div>`);
				}
			}
		});
	});
}); 