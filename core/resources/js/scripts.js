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

function setActive(elem) {
    elem.classList.add('active_header');
}

function resizeImgs(){
  imgs = document.getElementsByTagName('img');
  if (imgs[0].style.width == 'auto' || imgs[0].style.width == '') {
    for (var i = 0; i < imgs.length; i++) {
        imgs[i].style.width = "30%";
    }
  } else {
    for (var i = 0; i < imgs.length; i++) {
        imgs[i].style.width = "auto";
    }
  }
}
