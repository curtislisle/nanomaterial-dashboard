	    serviceUrl = "service/convertdata"
		$.ajax({
	        url: serviceUrl,
	        data: {
	        },
	        dataType: "json",
	        async: false,
	        type: "POST",
	        success: function (response) {
				console.log(response);
	        }
	    });

