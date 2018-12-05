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