function buildTable(tableID) {

  $(tableID).dynatable({
    table: {
        defaultColumnIdStyle: 'camelCase'
    },
  	features: {
  		paginate: true,
  		recordCount: true,
  		sorting: true
  	}
  });

  var dynatable = $(tableID).data('dynatable');
  dynatable.paginationPerPage.set(15);          // Show 20 records per page
  dynatable.paginationPage.set(1);              // Go to page 5
  dynatable.sorts.add("testCase", 1);
  dynatable.process();
}