/* nano_utilitiesUpload Application
 * 
 * This is an application that lets the user drag & drop VisualSonics CSV output files
 * onto the webpage and decide which attributes out of the datasets to upload to a
 * server database for compilation and later analysis
 * 
 * update revision:
 * 09/23/14 CRL 
 * 09/27/14 CRL added attribute template support (somewhat complex) so users can create multiple
 *              templates for which variables to store.  The template automatically updates the
 *              display and data storage is based on the display. 
 */

// start with an empty array that will contain a record of the CSV content of the files.  
var nano_utilities = {}
nano_utilities.fileArray = []
nano_utilities.fileCount = 0

// this is the location of the nanomaterial papers directory.  It is used by the utilities to 
// create and reset annotation files.  

nano_utilities.bratLocation = '/Users/clisle/code/brat-v1.3_Crunchy_Frog/data/nano_papers'

//------ beginning drag & drop support ----------------------------------------


function load(file) {
var xmlfilecontent = []
if (file==null)
  xmlfilecontent = "<header> <a>sometext</a> </header>"
  else {
  var reader = new FileReader();

  reader.onload = function(e) {
        // store the resulting file in browser local storage
        var fileDict = {}
        fileDict['name'] = file.name
        fileDict['contents'] = e.target.result
        nano_utilities.fileArray.push(fileDict)
        nano_utilities.fileCount = nano_utilities.fileCount*1 + 1
        console.log('nano_utilities file count now: ',nano_utilities.fileCount)
        //console.log(nano_utilities.fileArray)

        // copy the file to a python service for writing into the NLP directory
        for (var i = nano_utilities.fileArray.length - 1; i >= 0; i--) {

          data = {filename: nano_utilities.fileArray[i]['name'], 
                  filecontents: nano_utilities.fileArray[i]['contents'],
                  directory: nano_utilities.bratLocation};
          $.ajax({
              url: "service/uploadTexts",
              data: data,
              dataType: "json",
              success: function (response) {
                  console.log(response)
                  // we uploaded a new text file, so update the selection list so this file is included
                  initializeDocumentSelector();
              }
            }); 
          }      


  }
  reader.readAsText(file);
  //console.log(reader);
  }
}

// this is the callback invoked when a user drops a filename on the dropzone area.  It updates the visual
// content and calls the "load" function directly.  This is attached as a callback later in the file. 

function handleFileSelect(evt) {
        evt.stopPropagation();
        evt.preventDefault();
    //console.log(evt)
        var files = evt.dataTransfer.files; // FileList object.

        var output = [];
        for (var i = 0, f; f = files[i]; i++) {
          // load the tree that was dropped onto the drop pane and update the catalog of loaded
          // datasets in the UI
          load(f);
        }
}

// this function and its callback assignment below are needed for the drag action to work. This is
// called many times during the drag over the target, but we aren't taking any explicit action until
// a drop occurs. 
  
function handleDragOver(evt) {
        evt.stopPropagation();
        evt.preventDefault();
        evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}

//------ end drag & drop support ----------------------------------------


// code for handling transition between UI tabs

function openTab(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the link that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}




// check the annotation database and fill the selector with all the existing text files. If there
// are none, the service returns the value "default" as the first project name

function initializeDocumentSelector() {
        d3.select("#sourcetextnames").selectAll("option").remove();
        d3.json("service/listtexts", function (error, texts) {
            //console.log(texts,"\n");
            d3.select("#sourcetextnames").selectAll("option")
                .data(texts.result)
                .enter().append("option")
                .text(function (d) { return d; });
        });
}


function exportBratDataset() {

  var fileselector = d3.select("#sourcetextnames").node();
  var textname = fileselector.options[fileselector.selectedIndex].text;
  var materialname = document.getElementById('nlpforcename').value;
  var materialid =  document.getElementById('nlpforceid').value;
  var brattextdir = '/Users/clisle/code/brat-v1.3_Crunchy_Frog/data/nano_papers'

  // the filename will have a .txt extension, so lets trim this off and add the .ann for the
  // annotation file we want to search for
  annotationname = textname.substring(0,textname.indexOf('.'))+'.ann'

  // now call a python service to read the Brat standoff format and export a CSV table

  data = {filename: annotationname, materialname : materialname, materialid: materialid, directory: brattextdir};
  $.ajax({
      url: "service/exportBratAnnotation",
      data: data,
      dataType: "json",
      success: function (response) {
          console.log(response)
          write_NLP_Output(response)
      }
    });
}




function write_NLP_Output(content) {
  
    // write out arrays in CSV format
    
    var finalVal = '';
    for (var i = 0; i < content.result.length; i++) {
        var value = content.result[i];

        for (var j = 0; j < value.length; j++) {
            var innerValue =  value[j]===null?'':value[j].toString();
            var result = innerValue.replace(/"/g, '""');
            if (result.search(/("|,|\n)/g) >= 0)
                result = '"' + result + '"';
            if (j > 0)
                finalVal += ',';
            finalVal += result;
        }
        finalVal += '\n';
    }

    //console.log(finalVal);
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(finalVal));
    pom.setAttribute('download', 'nano_nlp_export.csv');
    pom.click();
}



function exportTableDataset() {

  var materialname = document.getElementById('tableforcename').value;
  var materialid =  document.getElementById('tableforceid').value;
  var dbname = 'NanoDB3'
  var collname = 'saved_pdf_output'

  data = {database: dbname, collection: collname, materialname : materialname, materialid: materialid};
  $.ajax({
      url: "service/exportPDFTable",
      data: data,
      dataType: "json",
      success: function (response) {
          console.log(response)
          write_Table_Output(response)
      }
    });
}


function write_Table_Output(content) {
  
    // write out arrays in CSV format
    
    var finalVal = '';
    for (var i = 0; i < content.result.length; i++) {
        var value = content.result[i];

        for (var j = 0; j < value.length; j++) {
            var innerValue =  value[j]===null?'':value[j].toString();
            var result = innerValue.replace(/"/g, '""');
            if (result.search(/("|,|\n)/g) >= 0)
                result = '"' + result + '"';
            if (j > 0)
                finalVal += ',';
            finalVal += result;
        }
        finalVal += '\n';
    }

    //console.log(finalVal);
    var pom = document.createElement('a');
    pom.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(finalVal));
    pom.setAttribute('download', 'nano_pdf_table_export.csv');
    pom.click();
}

// The user has selected to clear out the existing records from the PDF table extraction.  This is
// handled by a python service

function deletePDFTableRecords() {
      d3.json("service/deletePDFTable", function (error, texts) {
          console.log('deleted PDF Table records');
      });
}

function deleteAnnotations() {
  var fileselector = d3.select("#sourcetextnames").node();
  var textname = fileselector.options[fileselector.selectedIndex].text; 
  data = {filename: textname, textpath: nano_utilities.bratLocation};
  console.log(data)
  $.ajax({
      url: "service/deleteAnnotations",
      data: data,
      dataType: "json",
      success: function (response) {
          console.log(response)
      }
    });
}





function runAutoAnnotation() {

  var searchtarget = document.getElementById('targetword').value;
  var searchdist =  document.getElementById('maxdistance').value;
  var fileselector = d3.select("#sourcetextnames").node();
  var textname = fileselector.options[fileselector.selectedIndex].text;
  var brattextdir = '/Users/clisle/code/brat-v1.3_Crunchy_Frog/data/nano_papers'

  data = {filename: textname, textpath: brattextdir, SearchDistance : searchdist, targetword: searchtarget};
  $.ajax({
      url: "service/generateAnnotations",
      data: data,
      dataType: "json",
      success: function (response) {
          console.log(response)
      }
    });
}




// this function is called as soon as the page is finished loading
window.onload = function () {   

        // Setup the drag and drop listeners.
        var dropZone = document.getElementById('drop_zone');
        dropZone.addEventListener('dragover', handleDragOver, false);
        dropZone.addEventListener('drop', handleFileSelect, false);
        
        initializeDocumentSelector();

        // set a watcher on the UI buttons to take action when they are clicked
        
		d3.select("#processBratButton")
      .on("click", exportBratDataset);
    
		d3.select("#processTableButton")
      .on("click", exportTableDataset);
          
    d3.select("#deleteTableButton")
      .on("click",deletePDFTableRecords);
        
    d3.select("#doAnnotations")
      .on("click",runAutoAnnotation);

   d3.select("#deleteAnnotationsButton")
      .on("click",deleteAnnotations);

};
