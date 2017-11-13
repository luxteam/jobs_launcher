function buildTable(mydata) {

  var tr = document.getElementById('example-table').tHead.children[0];
    for (key in mydata[0]) {
    var th = document.createElement('th');
    th.innerHTML = key;
    tr.appendChild(th);
  }

  $('#example-table').dynatable({
  	dataset: {
  		records: mydata
  	}
  });

  var dynatable = $('#example-table').dynatable({
  	features: {
  		paginate: false,
  		recordCount: false,
  		sorting: false
  	}
  }).data('dynatable');

  var tools = [];
  var tests = [];
  var versions = [];

  $.each(mydata, function(index, value) {
      if ($.inArray(value.tool, tools) === -1) {
          tools.push(value.tool);
      }
      if ($.inArray(value.test_name, tests) === -1){
        tests.push(value.test_name);
      }
      if ($.inArray(value.render_version, versions) === -1){
        versions.push(value.render_version);
      }
  });

  var x = document.getElementById("search-tool");
  tools.forEach(function(item, i){
    var option = document.createElement("option");
    option.text = item;
    x.add(option);
  })

  var x = document.getElementById("search-render_version");
  versions.forEach(function(item, i){
    var option = document.createElement("option");
    option.text = item;
    x.add(option);
  })

  var x = document.getElementById("search-test_name");
  tests.forEach(function(item, i){
    var option = document.createElement("option");
    option.text = item;
    x.add(option);
  })

  $('#search-tool').change( function() {
  	var value = $(this).val();
  	if (value === "") {
  		dynatable.queries.remove("tool");
  	} else {
  		dynatable.queries.add("tool",value);
  	}
  	dynatable.process();
  });

  $('#search-render_version').change( function() {
  	var value = $(this).val();
  	if (value === "") {
  		dynatable.queries.remove("render_version");
  	} else {
  		dynatable.queries.add("render_version",value);
  	}
  	dynatable.process();
  });

  $('#search-test_name').change( function() {
    var value = $(this).val();
    if (value === "") {
      dynatable.queries.remove("test_name");
    } else {
      dynatable.queries.add("test_name",value);
    }
    dynatable.process();
  });


  // $('#search-example').dynatable({
  // 	features: {
  // 		paginate: false,
  // 		recordCount: false,
  // 		sorting: false
  // 	},
  // 	inputs: {
  // 		queries: $('#search-tool'),
  // 		queries: $('#search-render_version')
  // 	}
  // });

  var dynatable = $('#example-table').data('dynatable');
  dynatable.paginationPerPage.set(15); // Show 20 records per page
  dynatable.paginationPage.set(1); // Go to page 5
  dynatable.process();
}