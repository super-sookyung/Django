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
	$('#phone-verification-send-form').on('submit', event => {
		event.preventDefault();
		$(event.currentTarget).children().removeClass("is-invalid");
		$(".invalid-feedback").remove();
		$.ajax({
			type: "POST",
			url: sendPhoneVerificationCodeAPI,
			data: {'user_phone': $(".phone-verification-send-field").val(), 
				   'csrfmiddlewaretoken': csrfToken,
				   'check_phone_number_exists': true
				},
			dataType: 'json',
			success: function (data, textStatus) {
				if (data.code_sent == true) {
					var $phoneVerifyDiv = $('#phone-verification-div');
					$('#phone-verification-send-div').addClass("d-none disable");
					$phoneVerifyDiv.removeClass('d-none');
					$(".phone-verification-phone-field").val($(".phone-verification-send-field").val())
				} else {
					let responseData = $.parseJSON(data.errors);
					for (name in responseData) {
						for (var i in responseData[name]) {
							$(".phone-verification-send-field").addClass("is-invalid");
							$('#phone-verification-send-form-group-div').append(`<div class="invalid-feedback">` + responseData[name][i].message + `</div>`);
						}
					}
				}
			},
			error: function( jqXhr, textStatus, errorThrown ) {
				$('.phone-verification-send-field').addClass("is-invalid");
				$('#phone-verification-send-form-group-div').append(`<div class="invalid-feedback">Something wrong happened. Try Again</div>`);
			}
		});
	});

	// js for phone veryfiying code sending
	$('#phone-verification-form').on('submit', function(event, options) {
		options = options || {};

		$(event.currentTarget).children().removeClass("is-invalid");
		$(".invalid-feedback").remove();

		if (options.doDefault===true) {
			// run it with default so no need to do anything
		} else {
			event.preventDefault();
			$.ajax({
				type: "POST",
				url: phoneVerifyAPI,
				data: {'user_phone': $(".phone-verification-phone-field").val(),
					   'verification_code': $(".phone-verification-code-field").val(),  
					   'csrfmiddlewaretoken': csrfToken,
					   'check_phone_number_exists': true
					},
				dataType: 'json',
				success: function (data, textStatus) {
					if (data.verification_success == true) {
						$(event.currentTarget).trigger(event.type, {"doDefault": true});
					} else {
						let responseData = $.parseJSON(data.errors);
							for (name in responseData) {
								for (var i in responseData[name]) {
									$("input[name='" + name + "']").addClass("is-invalid");
									$(`<div class="invalid-feedback">` + responseData[name][i].message + `</div>`).insertAfter("input[name='" + name + "']");
							}
						}
					}
				},
				error: function( jqXhr, textStatus, errorThrown ) {
					// if redirect exists -- seems to be the only way to handle redirects with ajax
					if (jqXhr.status == 302) {
						window.location.replace(jqXhr.responseJSON.redirect);
					} else {
						//  if is not redirect something bad happened
						$('#phone-verification-send-field').addClass("is-invalid");
						$('#phone-verification-send-form-group-div').append(`<div class="invalid-feedback">Something wrong happened. Try Again</div>`);
					}
				}
			});
		}	
	});


});