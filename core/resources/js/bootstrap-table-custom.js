/**
 * Function for sorting test results by status. Uses 'data-sorter' attribute by bootstrap tables.
 * Case statuses (from highest to lowest sort priority):
 * - error - crash during test execution
 * - failed - pixel/time/ram diff too large
 * - passed - case executed without crushes; acceptable diff
 * - skipped - case wasn't launched
 */

var tables = $('.twoSetupTimes')
Array.prototype.forEach.call(tables, function(table) {
    $(table.id).on('column-switch.bs.table', function (field, checked) {
        alert(field)
        if (field.includes('Setup time')){
            $(this).getElementsByClassName('fullTimeTaken').prop("data-visible", checked)
            $(this).getElementsByClassName('syncTimeTaken').prop("data-visible", !checked)
        }
    })
})

function statusSorter(x, y) {
    var a = x.toLowerCase();
    var b = y.toLowerCase();

    if (a === b) return 0;

    if (a.includes('error')) {
        return -1;
    }

    if (a.includes('failed') && !b.includes('error')) {
        return -1;
    }

    if (a.includes('passed') && !b.includes('failed') && !b.includes('error')) {
        return -1;
    }

    return 1;
}

window.openFullImgSize = {
    'click img': function(e, value, row, index) {
        var renderImg = document.getElementById('renderedImgPopup');
        var baselineImg = document.getElementById('baselineImgPopup');

        document.getElementById('pairComparisonDiv').style.display = "";
        document.getElementsByName('increaseImgSizeButton')[0].disabled = false;
        document.getElementsByName('reduceImgSizeButton')[0].disabled = false;

        renderImg.src = "";
        baselineImg.src = "";

        var src_prefixes = ["thumb64_", "thumb256_"];
        renderImg.src = row.rendered_img.split('"')[1];

        if (row.baseline_img.includes("img")) {
            baselineImg.src = row.baseline_img.split('"')[1];
        }
        for (var i in src_prefixes) {
            renderImg.src = renderImg.src.replace(src_prefixes[i], "");
            if (row.baseline_img.includes("img")) {
                baselineImg.src = baselineImg.src.replace(src_prefixes[i], "");
            }
        }

        document.getElementById("imgsCompareTable").style.display = "";
        document.getElementById("imgsDiffTable").style.display = "none";
        document.getElementById('imgsDiffTable').is_reshalla = undefined;
        document.getElementById('thresholdRange').style.display = "none";
        document.getElementById('thresholdView').style.display = "none";

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
            var current_url = window.location.href;
            var url_parser = new URL(current_url);
            if (url_parser.searchParams.get("searchText")) {
                url_parser.searchParams.delete("searchText");
            }
            url_parser.searchParams.set("searchText", row.test_case);

            // duct tape for clipboard correct work
            node.setAttribute('value', url_parser.toString());
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
    for (key in row) {
        if (isFinite(parseFloat((value * 100 / row[key]).toFixed(2)))) {
            return (value * 100 / row[key]).toFixed(2) + " %"
        }
    }
    return "Skipped"
}

function performanceNormalizeStyleFormatter(value, row, index, field) {
    var values = [];
    for (key in row) {
        if (key != 0) {
            if (!isFinite(parseFloat(row[key]))) {values.push(parseFloat(1))}
            else {values.push(parseFloat(row[key]))}
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
    if (parseFloat(value) === 0.0) {
        opacity = 0;
    }

    return {
        classes: "",
        css: {"background-color": "rgba(" + red + ", " + green + ", " + blue + ", " + opacity + ")"}
    };
}

function searchTextInBootstrapTable(status) {
    $('.jsTableWrapper [id]').bootstrapTable('resetSearch', status);
}