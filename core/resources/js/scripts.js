function pixDifferenceCellStyle(value, row, index) {
  if (value > 0.0) {
        return {
            classes: 'badResult'
        };
    }
    return {};
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
