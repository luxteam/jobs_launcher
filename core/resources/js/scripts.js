function pixDifferenceCellStyle(value, row, index) {
  if (value > 30.0) {
        return {
            classes: 'badResult'
        };
    }
    return {};
}

function statusSorter(a, b) {
    console.log(a, b);
    if (a == b){
        console.log(a, b, 'equals');
        return 0;
    }
    if (a.includes("failed") || (a.includes("skipped") && !b.includes("failed"))) {
        console.log(a, b, '1');
        return 1;
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