   function loadpdf(pdfdata, fileName) {
	    serviceUrl = "service/loadpdf"
	    var defaulttables = [];
	    var defaultheader = [];
	    var inverttables = [];
	    var invertheader = [];
	    var disinvheader = "";
	    var disdefheader = "";
	    var respheader = "";
	    var respinvheader = "";
	    var table;
	    //console.log(pdfdata);
		$("#tableDiv").empty();
		$.ajax({
	        url: serviceUrl,
	        data: {
				data:JSON.stringify(pdfdata)
	        },
	        dataType: "json",
	        async: true,
	        type: "POST",
	        success: function (response) {
				//console.log(response);
				var tableHeaders;


				//console.log(titleValues);
				//console.log(response.characterList);
				
				for (var u = 0; u < response.header.length; u++) {
					tmpTitle = {};
					tmpTitle['title'] = String(response.header[u])
					tmpTitle['class'] = 'center'
					defaultheader.push(tmpTitle);
				}
				
				for (var v = 0; v < response.characterList.length; v++) {
					tmpArray = [];
					for (var u = 0; u < response.header.length; u++) {
						chk = response.header[u];
						if (response.characterList[v][chk]) {
							tmpArray.push(response.characterList[v][chk]);
						} else {
							tmpArray.push(" ");
						}
					}
					defaulttables.push(tmpArray);
				}
				//console.log(response.characterList);
				
				for (var u = 0; u < response.newheader.length; u++) {
					tmpTitle = {};
					tmpTitle['title'] = String(response.newheader[u])
					tmpTitle['class'] = 'center'
					invertheader.push(tmpTitle);
				}
				for (var v = 0; v < response.columncharacterList.length; v++) {
					tmpArray = [];
					for (var u = 0; u < response.newheader.length; u++) {
						chk = response.newheader[u];
						if (response.columncharacterList[v][chk]) {
							tmpArray.push(response.columncharacterList[v][chk]);
						} else {
							tmpArray.push(" ");
						}
					}
					inverttables.push(tmpArray);
				}
				var respheader = response.header;
				$.each(respheader, function(i, val){
					disdefheader += "<th>" + val + "</th>";
				});
				var respinvheader = response.newheader;
				$.each(respinvheader, function(i, val){
					disinvheader += "<th>" + val + "</th>";
				});
				loaddata();
				
				$('#selectbutton').click( function() {
					//t.$('tr:not(.selected)').each( function () {
					//	t.fnDeleteRow( $(this)[0], false );
					//} );
					var anSelected = fnGetSelected(table);
					table.fnDeleteRow(anSelected, false); 
					table.fnDraw();
					//console.log(t.$('tr.selected').data());
					//var oTT = TableTools.fnGetInstance( 'displayTable' );
					//var z = oTT.fnGetSelectedData();
					selectedArr = []
					table.$('tr').each( function () {
						selectedArr.push($(this).children(":first").text());		
						$(this).removeClass('selected');
					} );	
					insertArr = []	
					for (u = 0; u < defaulttables.length; u++) {
						for (v = 0; v < selectedArr.length; v++) {
							if (defaulttables[u][0] == selectedArr[v]) {
								insertArr.push(defaulttables[u]);
							}
						}
					}
					//console.log(insertArr);
					serviceUrl = "service/loaddata"
					$.ajax({
				        url: serviceUrl,
				        data: {
				           data: JSON.stringify(insertArr),
				           headerlist: JSON.stringify(respheader)
				        },
				        dataType: "json",
				        async: true,
				        success: function (response) {
							//console.log(response);
				        }
				    });
					
					
				});
				$('#revertbutton').click( function() {
					loaddata()
				});
				$('#savebutton').click( function() {
					console.log("save button");
					selectedArr = []
					table.$('tr').each( function () {
						selectedArr.push($(this).children(":first").text());		
					} );	
					insertArr = []	
					type = $("input[name=dataview]:radio").attr("value");
					headertmp = [];
					if (type == "default") {
						headertmp = defaultheader;
					} else {
						headertmp = invertheader;
					}
					longArr = []
					for (u = 0; u < defaulttables.length; u++) {
						fullArr = []
						for (v = 0; v < defaulttables[u].length; v++) {
							tmpitem = {};
							tmpitem[headertmp[v].title] = defaulttables[u][v];
							fullArr.push(tmpitem);
						}
						longArr.push(fullArr);
					}
					console.log(longArr);
					console.log($("input[name=dataview]:radio").attr("value"));
					orientation = $("input[name=dataview]:radio").attr("value");
					serviceUrl = "service/savedata"
					$.ajax({
				        url: serviceUrl,
				     	type: "POST",
				        data: {
				           data: JSON.stringify(longArr),
				           fileName: fileName,
				           orientation: orientation
				        },
				        dataType: "json",
				        async: true,
				        success: function (response) {
							alert("Saved");
				        }
				    });
				});

	        }
	    });
	//	$('.loader').hide();
	    function fnGetSelected( oTableLocal ) {
			return oTableLocal.$('tr:not(.selected)');
		}

		function loaddata() {
	            $("#tableDiv").empty();
				$("#tableDiv").append('<table id="displayTable" class="display" cellspacing="0" width="100%"><thead><tr>' + disdefheader + '</tr></thead></table>');
				$('#tableDiv').html( '<table cellpadding="0" cellspacing="0" border="1" class="display" id="displayTable"></table>' );
				table = $('#displayTable').dataTable( {
					"data": defaulttables,
					"columns" : defaultheader,
		            "order": [],
		            "bProcessing": true,
		            "bSort": false,
		            "scrollCollapse": true,
		            "paging": false,
		            "jQueryUI": true,
		            "bFilter":false
		
				});		
			$('#displayTable tbody').on( 'click', 'tr', function () {
			    $(this).toggleClass('selected');
			});
		}
		
		$("input[name=dataview]:radio").change(function () {
		    $("#tableDiv").empty();
			check = $(this).attr("value");
			if (check === "default") {
				$("#tableDiv").append('<table id="displayTable" class="display" cellspacing="0" width="100%"><thead><tr>' + disdefheader + '</tr></thead></table>');
				$('#tableDiv').html( '<table cellpadding="0" cellspacing="0" border="1" class="display" id="displayTable"></table>' );
				table = $('#displayTable').dataTable( {
					"data": defaulttables,
					"columns" : defaultheader,
		            "order": [],
		            "bProcessing": true,
		            "bSort": false,
		            "scrollCollapse": true,
		            "paging": false,
		            "jQueryUI": true,
		            "bFilter":false
		
				});			
			} else {
				$("#tableDiv").append('<table id="displayTable" class="display" cellspacing="0" width="100%"><thead><tr>' + disinvheader + '</tr></thead></table>');
				$('#tableDiv').html( '<table cellpadding="0" cellspacing="0" border="1" class="display" id="displayTable"></table>' );
				table = $('#displayTable').dataTable( {
					"data": inverttables,
					"columns" : invertheader,
		            "order": [],
		            "bProcessing": true,
		            "bSort": false,
		            "scrollCollapse": true,
		            "paging": false,
		            "jQueryUI": true,
		            "bFilter":false
		
				});	
			}
			$('#displayTable tbody').on( 'click', 'tr', function () {
			    $(this).toggleClass('selected');
			});
		});
	}

