/**
 * author: Alexander Lex - alex@seas.harvard.edu
 * author: Nils Gehlenborg - nils@hms.harvard.edu
 * author: Hendrik Srtobelt - strobelt@seas.harvard.edu
 * author: Romain Vuillemot - romain.vuillemot@gmail.com
 */

var dataSetDescriptions = []
var queryParameters = {};
var initCallback; // function to call when dataset is loaded
var globalCtx;

function initData(ctx, callback) {
    retrieveQueryParameters();
    setUpGUIElements();

    initCallback = callback;
    globalCtx = ctx;
    $.when($.ajax({ url: 'datasets.json', dataType: 'json' })).then(
        function (data, textStatus, jqXHR) {
            loadDataSetDescriptions(data);
        },
        function (data, textStatus, jqXHR) {
            //console.error('Error loading "' + this.url + '".');
            
        });

    /// registering custom dataset function
    $("#custom-dataset-submit").on('click', function () {
        var url = $("#custom-dataset-url").val();
        if (url != null) {
            loadDataSetDescriptions([url], true);
            queryParameters['dataset'] = dataSetDescriptions.length;
        }
    })

}

var handleDatasetDescription = function (result) {
    if (result != undefined) {
        dataSetDescriptions.push(result);
    }
}

var loadDataAfterAjaxComplete = function () {

}

var populateDSSelector = function () {

    // updating the drop-down box
    d3.select("#header-ds-selector")
        .selectAll('option').data(dataSetDescriptions).enter().append('option')
        .attr('value', function (d, i) {
            return i;
        })
        .attr('id', 'dataSetSelector')
        .text(function (d) {
            return d.name + ' ' + '(' + getNumberOfSets(d) + ' sets, ' + getNumberOfAttributes(d) + ' attributes' + ')';
        })
        .property('selected', function (d, i) {
            return (i === queryParameters['dataset'])
        });

    d3.select("#header-ds-selector").on('change', setQueryParametersAndChangeDataset);
}

function loadDataSetDescriptions(dataSetList) {

    var descriptions = [];
    //  var descriptionDeferreds = [];
    var requests = [];
    // launch requests to load data set descriptions
    for (var i = 0; i < dataSetList.length; ++i) {
        var url = dataSetList[i];
        requests.push($.ajax({ url: url, dataType: 'json', success: handleDatasetDescription}));
    }

    $.when.apply(undefined, requests).then(loadDataSetFromQueryParameters, handleDataSetError);
}

var handleDataSetError = function (jqXHR, textStatus, errorThrown) {
    alert("Could not load dataset. \n Error: " + errorThrown)
}

function loadDataSetFromQueryParameters() {
    populateDSSelector();
    $(EventManager).trigger("loading-dataset-started", { description: dataSetDescriptions[queryParameters['dataset']]  });
    //(queryParameters['dataset']);
    changeDataset();
}

var setQueryParametersAndChangeDataset = function () {
    queryParameters['dataset'] = this.options[this.selectedIndex].value;
    changeDataset();
}

/**
 * Replace or load a new dataset based on the dataset index in the query parameters
 */
var changeDataset = function () {

    $(EventManager).trigger("loading-dataset-started", { description: dataSetDescriptions[queryParameters['dataset']]  });

    sets.length = 0;
    subSets.length = 0;
    usedSets.length = 0;
    dataRows.length = 0;
    depth = 0;
    allItems.length = 0;
    attributes.length = 0;
    selectedAttributes = {};
    previousState = undefined;

    UpSetState.logicGroups = [];
    UpSetState.logicGroupChanged = true;

    loadDataSet(queryParameters['dataset']);

    updateQueryParameters();

    clearSelections();
}

// CRL - new dispatch to either call the original CSV input subsystem or process a URL returning
// JSON descriptions of the data.  

function loadDataSet(index) {
    // check if dataset is original file type, or JSON online type
    if (dataSetDescriptions[index]['datasource'] == 'remote') {
        processJsonDataSet(dataSetDescriptions[index]) 
    } else {
        processDataSet(dataSetDescriptions[index]);
    }
}

function processDataSet(dataSetDescription) {
    //processJsonDataSet(dataSetDescription)
    processTextDataSet(dataSetDescription)
}


function processJsonDataSet(dataSetDescription) {
    console.log('processing JSON data source')
    d3.json(dataSetDescription.file, function (data) {
        parseJsonDataSet(data, dataSetDescription);
        run();
    });
}

function processTextDataSet(dataSetDescription) {
    d3.text(dataSetDescription.file, 'text/csv', function (data) {
        parseDataSet(data, dataSetDescription);
        run();
    });
}

/**
 * Setting up the html GUI elements
 */
var setUpGUIElements = function () {

    var maxCardSpinner = document.getElementById('maxCardinality');
    var minCardSpinner = document.getElementById('minCardinality');

    var updateCardinality = function (e) {
        UpSetState.maxCardinality = maxCardSpinner.value;
        UpSetState.minCardinality = minCardSpinner.value;
        UpSetState.forceUpdate = true;
        run();
    };

    maxCardSpinner.addEventListener('input', updateCardinality);
    minCardSpinner.addEventListener('input', updateCardinality);

    var hideEmptiesCheck = document.getElementById('hideEmpties');

    var hideEmptiesFu = function (e) {
        UpSetState.hideEmpties = hideEmptiesCheck.checked;
        updateState();
        // TODO: need to call updateTransition instead, but this needs to be exposed first
        plot();
        plotSetOverview();
    };
    hideEmptiesCheck.addEventListener('click', hideEmptiesFu);

    var dataSelect = d3.select("#dataset-selector").append('div');

    var select = dataSelect.append('select').attr("id", "header-ds-selector");

    dataSelect.append('span').attr("class", "header-right").text('Choose Dataset');
}

function retrieveQueryParameters() {

    // Variables from query string
    var queryString = location.search.substring(1),
        re = /([^&=]+)=([^&]*)/g, m;

    // Creates a map with the query string parameters
    while (m = re.exec(queryString)) {
        queryParameters[decodeURIComponent(m[1])] = decodeURIComponent(m[2]);
    }

    queryParameters['dataset'] = parseInt(queryParameters['dataset']) || 0;
    queryParameters['duration'] = queryParameters['duration'] || 1000;
    queryParameters['orderBy'] = queryParameters['orderBy'] || "subsetSize"; // deviation, intersection, specific set
    queryParameters['grouping'] = queryParameters['grouping'] == "undefined" ? undefined : queryParameters['grouping'] || "groupBySet"; // groupByIntersectionSize, 
    queryParameters['selection'] = queryParameters['selection'] || "";
    // Missing item space query..

}

function updateQueryParameters() {
    var urlQueryString = "";
    if (Object.keys(queryParameters).length > 0) {
        urlQueryString = "?";
        for (var q in queryParameters) {
            urlQueryString += (q + "=" + queryParameters[q]) + "&";
        }
        urlQueryString = urlQueryString.substring(0, urlQueryString.length - 1);
    }

    history.replaceState({}, 'Upset', window.location.origin + window.location.pathname + urlQueryString);
}

function clearSelections() {
    selections = new SelectionList();
}

function createInitialSelection() {
    var selection = new Selection(allItems, new FilterCollection("#filters-controls", "#filters-list"));

    selections.addSelection(selection, true);
    selections.setActive(selection);
}

function run() {

    elementViewers.reset();

    setUpSubSets();
    // setUpGroupings();
    updateState();
    initCallback.forEach(function (callback) {
        callback();
    })
//    plot();

//    plotSetSelection();
    selections.setActive();
    //createInitialSelection();
    plotSetOverview({initialize: true});

    $(EventManager).trigger("loading-dataset-finished", { });
}

function getNumberOfSets(dataSetDescription) {
    var sets = 0;

    for (var i = 0; i < dataSetDescription.sets.length; ++i) {
        var setDefinitionBlock = dataSetDescription.sets[i];

        if (setDefinitionBlock.format === 'binary') {
            sets += setDefinitionBlock.end - setDefinitionBlock.start + 1;
        }
        else {
            console.error('Set definition format "' + setDefinitionBlock.format + '" not supported');
        }
    }

    return ( sets );
}

function getNumberOfAttributes(dataSetDescription) {
    return ( dataSetDescription.meta.length );
}

function getIdColumn(dataSetDescription) {
    for (var i = 0; i < dataSetDescription.meta.length; ++i) {
        if (dataSetDescription.meta[i].type === "id") {
            return dataSetDescription.meta[i].index;
        }
    }

    // id column not defined, assume 0
    return 0;
}

function parseDataSet(data, dataSetDescription) {

    var dsv = d3.dsv(dataSetDescription.separator, 'text/plain');

    // the raw set arrays
    var rawSets = [];
    var setNames = [];

    var file = dsv.parseRows(data);

    // the names of the sets are in the columns
    var header = file[dataSetDescription.header];

    // remove header
    file.splice(dataSetDescription.header, 1);

    // load set assignments
    var processedSetsCount = 0;
    for (var i = 0; i < dataSetDescription.sets.length; ++i) {
        // setDefn has a start and end index for an array of column values from the dataset, which are sets
        // this is a loop, because there might be several "groups" of set columns in the dataset.  Each group is processed
        // separately in a loop iteration.
        var setDefinitionBlock = dataSetDescription.sets[i];

        if (setDefinitionBlock.format === 'binary') {
            var setDefinitionBlockLength = setDefinitionBlock.end - setDefinitionBlock.start + 1;

            // initialize the raw set arrays
            for (var setCount = 0; setCount < setDefinitionBlockLength; ++setCount) {
                rawSets.push(new Array());
            }

            // this is a mapping function which runs through all rows of the dataset and returns the binary values
            // of the columns in this set definition block. For example start=1, end=6 will return an array for each
            // line of the file.  Each entry will be an array of 6 entries, for the 6 sets.

            var rows = file.map(function (row, rowIndex) {
                return row.map(function (value, columnIndex) {

                    if (columnIndex >= setDefinitionBlock.start && columnIndex <= setDefinitionBlock.end) {
                        var intValue = parseInt(value, 10);

                        if (isNaN(intValue)) {
                            console.error('Unable to convert "' + value + '" to integer (row ' + rowIndex + ', column ' + columnIndex + ')');
                        }

                        return intValue;
                    }

                    return null;
                });
            });

            // now "rows" contains the set description from above

            // iterate over columns defined by this set definition block
            for (var r = 0; r < rows.length; r++) {
                // increment number of items in data set
                // only increment depth when we are processing the first set definition block (we will already iterate overall rows)
                if (i === 0) {
                    allItems.push(depth++);
                }

                // this loop adds the set values across the different block definitions into the "rawSets" array
                for (var s = 0; s < setDefinitionBlockLength; ++s) {
                    rawSets[processedSetsCount + s].push(rows[r][setDefinitionBlock.start + s]);

                    if (r === 1) {
                        setNames.push(header[setDefinitionBlock.start + s]);
                    }
                }
            }

            processedSetsCount += setDefinitionBlockLength;
        }
        else {
            console.error('Set definition format "' + setDefinitionBlock.format + '" not supported');
        }
    }

    // initialize sets and set IDs
    // the Set() type is defined in dataStructure.js and includes the set value data and  associated metadata. the
    // variable "setList" and "attributes" are filled by the loading process. 

    var setPrefix = "S_";
    //var setID = 1;
    for (var i = 0; i < rawSets.length; i++) {
        var combinedSets = Array.apply(null, new Array(rawSets.length)).map(Number.prototype.valueOf, 0);
        combinedSets[i] = 1;
        var set = new Set(setPrefix + i, setNames[i], combinedSets, rawSets[i]);
        setIdToSet[setPrefix + i] = set;
        sets.push(set);
        if (i < nrDefaultSets) {
            set.isSelected = true;
            usedSets.push(set);
        }
        // setID = setID << 1;
    }

    // initialize attribute data structure. 
    attributes.length = 0;
    for (var i = 0; i < dataSetDescription.meta.length; ++i) {
        var metaDefinition = dataSetDescription.meta[i];

        attributes.push({
            name: metaDefinition.name || header[metaDefinition.index],
            type: metaDefinition.type,
            values: [],
            sort: 1
        });
    }

    // add implicit attributes
    var setCountAttribute = {
        name: 'Set Count',
        type: 'integer',
        values: [],
        sort: 1,
        min: 0
    };

       

    // rawSets contains an Array of elements for each "set" defined in this data.  For example, for 
    // Simpsons, 6 sets ('Blue Hair','school', etc...).  For each set, an array of all elements is created
    // and a 1 is written to the array if the element is in this particular set.

    for (var d = 0; d < depth; ++d) {
        var setCount = 0;
        for (var s = 0; s < rawSets.length; s++) {
            // added gate to stop dirty (non 0 or 1) data from corrupting the set total
            if ( (typeof rawSets[s][d]) ==='number') {
                setCount += rawSets[s][d];
            }
        }
        setCountAttribute.values[d] = setCount;
    }
    // For each element, calculate how many sets the element belongs to.  Then add an array of these
    // totals to the attributes of the dataset, calling it setCountAttribute.
    attributes.push(setCountAttribute);

    var setsAttribute = {
        name: 'Sets',
        type: 'sets',
        values: [],
        sort: 1
    };


    // fill the setsAttribute with an aggregated list, where all set membership for each element is combined into
    // a list.  A single Array is in setsAttribute.value.  This array has an entry for each data element.  The value is a
    // list of which sets the element is contained in.  Sets are listed by id (e.g. "S_0", "S_1", etc.)

    for (var d = 0; d < depth; ++d) {
        var setList = [];
        for (var s = 0; s < rawSets.length; s++) {
            if (rawSets[s][d] === 1) {
                //setList.push(Math.floor(Math.pow(2, s)));
                setList.push(sets[s].id)
            }
        }
        setsAttribute.values[d] = setList;
    }
    attributes.push(setsAttribute);

    // load meta data
    // This fills in the names of all the sets in the attributes structure.  Before this loop, the attributes[0] had an
    // empty Name array.  Afterwards, it was filled with the proper named values for each set. 

    for (var i = 0; i < dataSetDescription.meta.length; ++i) {
        var metaDefinition = dataSetDescription.meta[i];

        attributes[i].values = file.map(function (row, rowIndex) {
            var value = row[metaDefinition.index];
            switch (metaDefinition.type) {
                case 'integer':
                    var intValue = parseInt(value, 10);
                    if (isNaN(intValue)) {
                        console.error('Unable to convert "' + value + '" to integer.');
                        return NaN;
                    }
                    return intValue;
                case 'float':
                    var floatValue = parseFloat(value, 10);
                    if (isNaN(floatValue)) {
                        console.error('Unable to convert "' + value + '" to float.');
                        return NaN;
                    }
                    return floatValue;
                case 'id':
                // fall-through
                case 'string':
                // fall-through
                default:
                    return value;
            }

        });
    }

    var max

    // add meta data summary statistics
    for (var i = 0; i < attributes.length; ++i) {

        if (attributes[i].type === "float" || attributes[i].type === "integer") {
            // explictly defined attributes might have user-defined ranges
            if (i < dataSetDescription.meta.length) {
                attributes[i].min = dataSetDescription.meta[i].min || Math.min.apply(null, attributes[i].values);
                attributes[i].max = dataSetDescription.meta[i].max || Math.max.apply(null, attributes[i].values);
            }
            // implicitly defined attributes
            else {
                attributes[i].min = attributes[i].min || Math.min.apply(null, attributes[i].values);
                attributes[i].max = attributes[i].max || Math.max.apply(null, attributes[i].values);
            }
        }
    }

    UpSetState.maxCardinality = attributes[attributes.length - 2].max;
    if (isNaN(UpSetState.maxCardinality)) {
        // fixme hack to make it work without attributes
        UpSetState.maxCardinality = sets.length;
    }
    var maxCardSpinner = document.getElementById('maxCardinality');
    maxCardSpinner.value = UpSetState.maxCardinality;
    maxCardSpinner.max = UpSetState.maxCardinality;
    var minCardSpinner = document.getElementById('minCardinality');
    minCardSpinner.max = UpSetState.maxCardinality;

    updateDatasetInformation(dataSetDescription)

}


// CRL - add JSON parsing option


function parseJsonDataSet(data, dataSetDescription) {

    console.log('parseJsonDataSet')
    console.log('data=',data)

    // the raw set arrays
    var rawSets = [];
    var setNames = [];

    var file = data['data'];

    // the names of the sets are in the columns
    var header = data['header'];


    // initialize the rawSets variable to a set of empty arrays, one for each defined "set"
    for (var setCount = 0; setCount < dataSetDescription['setlist'].length; ++setCount) {
        rawSets.push(new Array());
    }

    // loop through each set defined in the 'setlist': then create an array in rawSets which has an array for each 
    // set.   the values for each entry correspond to what values for this particular setname each entry in the dataset has

    for (var setCount = 0; setCount < dataSetDescription['setlist'].length; setCount++) {
        var col = dataSetDescription['setlist'][setCount]
        for (var datarow=0; datarow < file.length; datarow++) {
            rawSets[setCount].push(file[datarow][col])
        }
    }   


    console.log('rawSets:',rawSets)

/*
            // iterate over columns defined by this set definition block
            for (var r = 0; r < rows.length; r++) {
                // increment number of items in data set
                // only increment depth when we are processing the first set definition block (we will already iterate overall rows)
                if (i === 0) {
                    allItems.push(depth++);
                }

                for (var s = 0; s < setDefinitionBlockLength; ++s) {
                    rawSets[processedSetsCount + s].push(rows[r][setDefinitionBlock.start + s]);

                    if (r === 1) {
                        setNames.push(header[setDefinitionBlock.start + s]);
                    }
                }
            }

            processedSetsCount += setDefinitionBlockLength;
*/
    // record how many items are in the dataset
    for (var i=0;i<file.length;i++) {
        allItems.push(depth++)
    }

    // for each set definition, add its name to the variable collecting the names
    for (var setCount = 0; setCount < dataSetDescription['setlist'].length; setCount++) {
        setNames.push(dataSetDescription['setlist'][setCount])
    }


    // initialize sets and set IDs
    var setPrefix = "S_";
    //var setID = 1;
    for (var i = 0; i < rawSets.length; i++) {
        var combinedSets = Array.apply(null, new Array(rawSets.length)).map(Number.prototype.valueOf, 0);
        combinedSets[i] = 1;
        var set = new Set(setPrefix + i, setNames[i], combinedSets, rawSets[i]);
        setIdToSet[setPrefix + i] = set;
        sets.push(set);
        if (i < nrDefaultSets) {
            set.isSelected = true;
            usedSets.push(set);
        }
        // setID = setID << 1;
    }

    // initialize attribute data structure
    attributes.length = 0;
    for (var i = 0; i < dataSetDescription.meta.length; ++i) {
        var metaDefinition = dataSetDescription.meta[i];

        attributes.push({
            name: metaDefinition.name || header[metaDefinition.index],
            type: metaDefinition.type,
            values: [],
            sort: 1
        });
    }

    // add implicit attributes
    var setCountAttribute = {
        name: 'Set Count',
        type: 'integer',
        values: [],
        sort: 1,
        min: 0
    };

    for (var d = 0; d < depth; ++d) {
        var setCount = 0;
        for (var s = 0; s < rawSets.length; s++) {
            // added gate to stop dirty (non 0 or 1) data from corrupting the set total
            if ( (typeof rawSets[s][d]) ==='number') {            
                setCount += rawSets[s][d];
            }
        }
        setCountAttribute.values[d] = setCount;
    }
    attributes.push(setCountAttribute);

    var setsAttribute = {
        name: 'Sets',
        type: 'sets',
        values: [],
        sort: 1
    };

    for (var d = 0; d < depth; ++d) {
        var setList = [];
        for (var s = 0; s < rawSets.length; s++) {
            if (rawSets[s][d] === 1) {
                //setList.push(Math.floor(Math.pow(2, s)));
                setList.push(sets[s].id)
            }
        }
        setsAttribute.values[d] = setList;
    }
    attributes.push(setsAttribute);

    // load meta data
    for (var i = 0; i < dataSetDescription.meta.length; ++i) {
        var metaDefinition = dataSetDescription.meta[i];

        /*
        attributes[i].values = file.map(function (row, rowIndex) {
            var value = row[metaDefinition.index];
            switch (metaDefinition.type) {
                case 'integer':
                    var intValue = parseInt(value, 10);
                    if (isNaN(intValue)) {
                        console.error('Unable to convert "' + value + '" to integer.');
                        return NaN;
                    }
                    return intValue;
                case 'float':
                    var floatValue = parseFloat(value, 10);
                    if (isNaN(floatValue)) {
                        console.error('Unable to convert "' + value + '" to float.');
                        return NaN;
                    }
                    return floatValue;
                case 'id':
                // fall-through
                case 'string':
                // fall-through
                default:
                    return value;
            }

        });
        */

        // the original design used a map over the file, but we are using mongo attribute keywords
        // since mongo may not return them in a specific order.  This loop visits every entry in the 
        // dataset and appends a looked up value to the attributes array.  When this loop is finished, the 
        // values of a particular attribute have been assigned to the attributes array.  Since this loop is inside, 
        // a loop that examines the attributes one at a time, all values will be flushed out when the outer loop 
        // is finished. 

        for (var row = 0; row < file.length; row++) {
            var value = file[row][metaDefinition['name']]
             switch (metaDefinition.type) {
                case 'integer':
                    var intValue = parseInt(value, 10);
                    if (isNaN(intValue)) {
                        console.error('Unable to convert "' + value + '" to integer.');
                        attributes[i].values.push(0);
                    } 
                    attributes[i].values.push(intValue);
                    break;
                case 'float':
                    var floatValue = parseFloat(value, 10);
                    if (isNaN(floatValue)) {
                        console.error('Unable to convert "' + value + '" to float.');
                        // in Nano Database this was encountered. replace with a flag value (-1)
                        if (value == 'Graphically Represented') {
                            value = -1
                        }
                        attributes[i].values.push(0);
                    }
                    attributes[i].values.push(floatValue);
                    break;
                case 'id':
                // fall-through
                case 'string':
                // fall-through
                default:
                   attributes[i].values.push(value)
            }
        }

    }

    var max

    // add meta data summary statistics
    for (var i = 0; i < attributes.length; ++i) {

        if (attributes[i].type === "float" || attributes[i].type === "integer") {
            // explictly defined attributes might have user-defined ranges
            if (i < dataSetDescription.meta.length) {
                attributes[i].min = dataSetDescription.meta[i].min || Math.min.apply(null, attributes[i].values);
                attributes[i].max = dataSetDescription.meta[i].max || Math.max.apply(null, attributes[i].values);
            }
            // implicitly defined attributes
            else {
                attributes[i].min = attributes[i].min || Math.min.apply(null, attributes[i].values);
                attributes[i].max = attributes[i].max || Math.max.apply(null, attributes[i].values);
            }
        }
    }

    UpSetState.maxCardinality = attributes[attributes.length - 2].max;
    if (isNaN(UpSetState.maxCardinality)) {
        // fixme hack to make it work without attributes
        UpSetState.maxCardinality = sets.length;
    }
    var maxCardSpinner = document.getElementById('maxCardinality');
    maxCardSpinner.value = UpSetState.maxCardinality;
    maxCardSpinner.max = UpSetState.maxCardinality;
    var minCardSpinner = document.getElementById('minCardinality');
    minCardSpinner.max = UpSetState.maxCardinality;

    updateDatasetInformation(dataSetDescription)

}


// update the UI elements to show the content of the currently loaded dataset.

var updateDatasetInformation = function (dataSetDescription) {

    var infoBox = $('#dataset-info-content');
    infoBox.empty();
    //infoBox.append('<hr><br />');
    infoBox.append('<p style="padding-bottom: 5px">');
    infoBox.append("<b>Name:</b> " + dataSetDescription.name + "<br />");
    infoBox.append("<b># Sets:</b> " + sets.length + "<br />");
    infoBox.append("<b># Attributes</b>: " + attributes.length + "<br />");
    infoBox.append("<b># Elements:</b> " + depth + "<br />");
    infoBox.append('</p> <p style="padding-bottom: 10px">');
    if (dataSetDescription.author) {
        infoBox.append("<b>Author</b>: " + dataSetDescription.author + "<br />");
    }
    if (dataSetDescription.description) {
        infoBox.append("<b>Description:</b> <br />" + dataSetDescription.description + "<br />");
    }
    if (dataSetDescription.source) {
        if (dataSetDescription.source.indexOf("http://") == 0) {
            var urlText = dataSetDescription.source;
            var numCharacters = 22;
            if (urlText.length > numCharacters) {
                urlText = urlText.substring(0, numCharacters) + ".."
            }

            infoBox.append("<b>Source:</b> <br /><a href=\"" + dataSetDescription.source + "\">" + urlText + "</a><br />");

        } else {
            infoBox.append("<b>Source:</b> <br />" + dataSetDescription.source + "<br />");
        }
    }

    infoBox.append('</p>');

}

function createSignature(listOfUsedSets, listOfSets) {
    return listOfUsedSets.map(function (d) {
        return (listOfSets.indexOf(d) > -1) ? 1 : 0
    }).join("")

}

function setUpSubSets() {

    $(EventManager).trigger("computing-subsets-started", undefined);

    combinations = Math.pow(2, usedSets.length) - 1;

    subSets.length = 0;

    var aggregateIntersection = {}

    var listOfUsedSets = usedSets.map(function (d) {
        return d.id
    })

    var setsAttribute = attributes.filter(function (d) {
        return d.type == "sets"
    })[0];

    var signature = "";

    var itemList;
    //HEAVY !!!
    setsAttribute.values.forEach(function (listOfSets, index) {
        signature = createSignature(listOfUsedSets, listOfSets)
        itemList = aggregateIntersection[signature];
        if (itemList == null) {
            aggregateIntersection[signature] = [index];
        } else {
            itemList.push(index);
        }
    })

    // used Variables for iterations
    var tempBitMask = 0;
    var usedSetLength = usedSets.length
    var combinedSetsFlat = "";
    var actualBit = -1;
    var names = [];

    if (usedSetLength > 20) { // TODo HACK !!!!
        Object.keys(aggregateIntersection).forEach(function (key) {
            var list = aggregateIntersection[key]

            var combinedSets = key.split("");

            //combinedSetsFlat = combinedSets.join("");

//            if (card>UpSetState.maxCardinality) continue;//UpSetState.maxCardinality = card;
//            if (card<UpSetState.minCardinality) continue;//UpSetState.minCardinality = card;

            names = [];
            var expectedValue = 1;
            var notExpectedValue = 1;
            // go over the sets
            combinedSets.forEach(function (d, i) {
                    if (d == 1) { // if set is present
                        names.push(usedSets[i].elementName);
                        expectedValue = expectedValue * usedSets[i].dataRatio;
                    } else {
                        notExpectedValue = notExpectedValue * (1 - usedSets[i].dataRatio);
                    }
                }
            );

            //        console.log(expectedValue, notExpectedValue);
            expectedValue *= notExpectedValue;

            //        console.log(combinedSetsFlat);

            var name = "";
            if (names.length > 0) {
                name = names.reverse().join(" ") + " " // not very clever
            }

            //        var arghhList = Array.apply(null,new Array(setsAttribute.values.length)).map(function(){return 0})
            //        list.forEach(function(d){arghhList[d]=1});

//            console.log(parseInt(key,2), name, combinedSets, list, expectedValue);

            var subSet = new SubSet(bitMask, name, combinedSets, list, expectedValue);
            subSets.push(subSet);

        })

    } else {
        for (var bitMask = 0; bitMask <= combinations; bitMask++) {
            tempBitMask = bitMask;//originalSetMask

            var card = 0;
            var combinedSets = Array.apply(null, new Array(usedSetLength)).map(function () {  //combinedSets
                actualBit = tempBitMask % 2;
                tempBitMask = (tempBitMask - actualBit) / 2;
                card += actualBit;
                return +actualBit
            }).reverse() // reverse not necessary.. just to keep order

            combinedSetsFlat = combinedSets.join("");

            if (card > UpSetState.maxCardinality) continue;//UpSetState.maxCardinality = card;
            if (card < UpSetState.minCardinality) continue;//UpSetState.minCardinality = card;

            names = [];
            var expectedValue = 1;
            var notExpectedValue = 1;
            // go over the sets
            combinedSets.forEach(function (d, i) {


                    //                console.log(usedSets[i]);
                    if (d == 1) { // if set is present
                        names.push(usedSets[i].elementName);
//                    expectedValue*=expectedValueForOneSet;
                        expectedValue = expectedValue * usedSets[i].dataRatio;
                    } else {
                        notExpectedValue = notExpectedValue * (1 - usedSets[i].dataRatio);
                    }
                }
            );

            //        console.log(expectedValue, notExpectedValue);
            expectedValue *= notExpectedValue;

            //        console.log(combinedSetsFlat);
            var list = aggregateIntersection[combinedSetsFlat];
            if (list == null) {
                list = [];
            }

            var name = "";
            if (names.length > 0) {
                name = names.reverse().join(" ") + " " // not very clever
            }

            //        var arghhList = Array.apply(null,new Array(setsAttribute.values.length)).map(function(){return 0})
            //        list.forEach(function(d){arghhList[d]=1});

            var subSet = new SubSet(bitMask, name, combinedSets, list, expectedValue);
            subSets.push(subSet);
        }
    }
    aggregateIntersection = {};

//    var subSet = new SubSet(originalSetMask, name, combinedSets, combinedData, expectedValue);
//    subSets.push(subSet);
//
//    for (var i = 0; i <= combinations; i++) {
//        makeSubSet(i)
//    }

    $(EventManager).trigger("computing-subsets-finished", undefined);

}

function updateSetContainment(set, refresh) {
    if (!set.isSelected) {
        set.isSelected = true;
        usedSets.push(set);
        $(EventManager).trigger("set-added", { set: set });
    }
    else {
        set.isSelected = false;

        var index = usedSets.indexOf(set);
        if (index > -1) {
            usedSets.splice(index, 1);
            $(EventManager).trigger("set-removed", { set: set });
        }
    }

    if (refresh) {
        subSets.length = 0;
        dataRows.length = 0;
        setUpSubSets();
        //  setUpGroupings();
        previousState = undefined;
        updateState();

//        ctx.updateHeaders();
//
//        plot();
//        plotSetSelection();
        plotSetOverview();
        initCallback.forEach(function (callback) {
            callback();
        })

//        ctx.svg.attr("width", ctx.w)
//        d3.selectAll(".svgGRows, .foreignGRows").attr("width", ctx.w)
//        d3.selectAll(".backgroundRect").attr("width", ctx.w - ctx.leftOffset)
    }
}

function addSet(set) {

}

function removeSet(set) {
    console.log('Not implemented');
}
