// error - means crash durin test execution
// failed - pix /time/vram diff
// skipped - commented case
function statusSorter(a, b) {
    if (a == b) return 0;

    if (a.includes('error')) {
        return 1;
    }

    if (a.includes('failed') && !b.includes('error')) {
        return 1;
    }

    if (a.includes('skipped') && !b.includes('failed') && !b.includes('error')) {
        return 1;
    }

    return -1;
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

function metaAJAX(value, row, index, field) {
    return value.replace('data-src', 'src');
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