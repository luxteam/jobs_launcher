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