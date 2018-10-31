//TODO: add NOK status to sorting
//TODO: fix sorting
function statusSorter(a, b) {
    if (a == b) {
        return 0;
    }

    if (a.includes('failed') || a.includes('skipped') && (!b.includes('failed') && !b.includes('skipped'))) {
        return 1;
    }

    if (a.includes('failed') && b.includes('skipped')) {
        return 1;
    }

    a = a.split('<br>');
    b = b.split('<br>');

    if (a[0] == b[0]) {
        return a[2] > b[2] ? 1 : -1;
    }

    return -1;
}

function setActive(elem) {
    elem.classList.add('active_header');
}

function resizeAllImg(){
  imgs = document.getElementsByClassName('resizedImg');
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

$.extend($.expr[':'], {
  'containsCI': function(elem, i, match, array)
  {
    return (elem.textContent || elem.innerText || '').toLowerCase()
    .indexOf((match[3] || "").toLowerCase()) >= 0;
  }
});

function resizeImg(img){
    if (img.style.width == ""){
        img.style.width = "30%";
    }

    if (img.style.width == "30%"){
        img.style.width = "100%";
    } else {
        img.style.width = "30%";
    }
}

window.openFullImgSize = {
    'click img': function(e, value, row, index) {
        var renderImg = document.getElementById('renderedImgPopup');
        var baselineImg = document.getElementById('baselineImgPopup');

        renderImg.src = "";
        baselineImg.src = "";

        renderImg.src = row.rendered_img.split('"')[1].replace("thumb64_", "");
        try {
            baselineImg.src = row.baseline_img.split('"')[1].replace("thumb64_", "");
        } catch(e){
        }

        openModalWindow('imgsModal');
    }
}

function timeFormatter(value, row, index, field) {
    var time = new Date(null);
    time.setSeconds(value);
    return time.toISOString().substr(11, 8);
}

function metaAJAX(value, row, index, field) {
    return value.replace('data-src', 'src');
}

function openModalWindow(id) {
    var modal = document.getElementById(id);
    modal.style.display = "block";

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

function closeModalWindow(id) {
    document.getElementById(id).style.display = "none";
}

function increaseImgSize() {
    var renderImg = document.getElementById('renderedImgPopup');
    var baselineImg = document.getElementById('baselineImgPopup');

    renderImg.width += 50;
    baselineImg.width +=50;
}

function reduceImgSize() {
    var renderImg = document.getElementById('renderedImgPopup');
    var baselineImg = document.getElementById('baselineImgPopup');

    renderImg.width -= 50;
    baselineImg.width -=50;
}

//TODO: finish custom img size
function setImgSize() {
    var renderImg = document.getElementById('renderedImgPopup');
    var baselineImg = document.getElementById('baselineImgPopup');
    var widthValue = document.getElementsByName('inputImgSize')[0].value;

    renderImg.width = widthValue;
    baselineImg.width = widthValue;
}

window.copyTestCaseName = {
    'click button': function(e, value, row, index) {

        try {
            var node = document.createElement('input');
            //TODO: if previous link has vars - store it too
            var normalized_link = window.location.hostname + window.location.pathname + "?searchText=";
            node.setAttribute('value', normalized_link + row.test_case);
            document.body.appendChild(node);
            node.select();
            document.execCommand('copy');
            node.remove();
            // popup with status for user
            infoBox("Link copied to clipboard.")
        } catch(e) {
            infoBox("Can't copy to clipboard.")
        }
    }
}

//TODO: add var for configure box color
function infoBox(message) {
    $("#infoBox").html("<p>" + message + "</p>");
    $("#infoBox").fadeIn('slow');
    setTimeout(function(){$("#infoBox").fadeOut('slow');} , 2000);
}

function getQueryVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0; i < vars.length; i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable) {
            return pair[1];
        }
    }
    return(false);
}

jQuery(document).ready( function() {
    var searchText = getQueryVariable('searchText');
    if (searchText) {
        $('.jsTableWrapper [id]').bootstrapTable('resetSearch', searchText);
    }
});

$(document).ready(function init(){
    $( "h3:containsCI('NVIDIA')" ).css( "color", "rgba(118, 185, 0, 1)" );
    $( "table.baseTable th:containsCI('NVIDIA')" ).css( "color", "rgba(118, 185, 0, 1)" );
    $( "h3:containsCI('GeForce')" ).css( "color", "rgba(118, 185, 0, 1)"
    );
    $( "table.baseTable th:containsCI('GeForce')" ).css( "color", "rgba(118, 185, 0, 1)" );

    $( "h3:containsCI('Radeon')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "table.baseTable th:containsCI('Radeon')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "h3:containsCI('AMD')" ).css( "color", "rgba(92, 136, 200, 1)" );
    $( "table.baseTable th:containsCI('AMD')" ).css( "color", "rgba(92, 136, 200, 1)" );
});
