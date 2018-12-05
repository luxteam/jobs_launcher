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

function timeFormatter(value, row, index, field) {
    var time = new Date(null);
    time.setSeconds(value);
    return time.toISOString().substr(11, 8);
}

function openModalWindow(id) {
    var modal = document.getElementById(id);
    modal.style.display = "flex";

    var diffCanvas = document.getElementById('imgsDiffTable');
    var imagesTable = document.getElementById("imgsCompareTable");

    if (diffCanvas && diffCanvas.style.display == "block") {
        imagesTable.style.display = "";
        diffCanvas.style.display = "none";
    }

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
    $("#imgsDifferenceCanvas").css("width", function( index, value ) {
	    return parseInt(value, 10) + document.documentElement.clientWidth / 100 * 5;
    });

    $("#renderedImgPopup").css("width", function( index, value ) {
	    return parseInt(value, 10) + document.documentElement.clientWidth / 100 * 5;
    });

    $("#baselineImgPopup").css("width", function( index, value ) {
	    return parseInt(value, 10) + document.documentElement.clientWidth / 100 * 5;
    });
}

function reduceImgSize() {
    $("#imgsDifferenceCanvas").css("width", function( index, value ) {
	    return parseInt(value, 10) - document.documentElement.clientWidth / 100 * 5;
    });

    $("#renderedImgPopup").css("width", function( index, value ) {
	    return parseInt(value, 10) - document.documentElement.clientWidth / 100 * 5;
    });

    $("#baselineImgPopup").css("width", function( index, value ) {
	    return parseInt(value, 10) - document.documentElement.clientWidth / 100 * 5;
    });
}

//TODO: finish custom img size
function setImgSize() {
    var renderImg = document.getElementById('renderedImgPopup');
    var baselineImg = document.getElementById('baselineImgPopup');
    var widthValue = document.getElementsByName('inputImgSize')[0].value;

    renderImg.width = widthValue;
    baselineImg.width = widthValue;
}

function infoBox(message, bgcolor=false) {
    $("#infoBox").html("<p>" + message + "</p>");
    $("#infoBox").fadeIn('slow');
    if (bgcolor) {
        $("#infoBox").css({
            "background-color": bgcolor,
            "opacity": 0.4
            });
    }

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

function performanceNormalizeFormatter(value, row, index, field) {
    return (value * 100 / row[1]).toFixed(2) + " %";
}

function performanceNormalizeStyleFormatter(value, row, index, field) {
    var values = [];
    for (key in row) {
        if (key.indexOf('_') == -1 && key != 0) {
            values.push(parseFloat(row[key]));
        }
    }

    var max = Math.max.apply(Math, values);

    var redInit = 180;
    var greenInit = 215;
    var blueInit = 125;

    var redWorst = 255;
    var greenWorst = 113;
    var blueWorst = 119;

    var redBest = 110;
    var greenBest = 190;
    var blueBest = 120;

    if (field == 1) {
        var red = redInit;
        var blue = blueInit;
        var green = greenInit;
    } else if (parseFloat(value) > values[0]) {
        var red = Math.round(redInit + (redWorst - redInit)* value/max);
        var green = Math.round(greenInit + (greenWorst - greenInit)* value/max);
        var blue = Math.round(blueInit + (blueWorst - blueInit)* value/max);
    } else {
        var red = Math.round(redInit + (redBest - redInit)* value/max);
        var green = Math.round(greenInit + (greenBest - greenInit)* value/max);
        var blue = Math.round(blueInit + (blueBest - blueInit)* value/max);
    }

    var opacity = 1;
    if (parseFloat(value) == 0.0) {
        opacity = 0;
    }

    return {
        classes: "",
        css: {"background-color": "rgba(" + red + ", " + green + ", " + blue + ", " + opacity + ")"}
    };
}