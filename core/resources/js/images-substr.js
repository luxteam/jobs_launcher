function showImagesSubtraction(baselineId, renderId) {

    // TODO: catch case with empty images
    // TODO: didn't repeat canvas creation if the same images compare
    var diffCanvas = document.getElementById('imgsDifferenceCanvas');
    var imagesTable = document.getElementById("imgsCompareTable");
    var diffTable = document.getElementById('imgsDiffTable');

    if (diffCanvas && diffTable.style.display == "block") {
        imagesTable.style.display = "";
        diffTable.style.display = "none";
        return;
    }
    else if (diffCanvas && diffTable.style.display == "none") {
        diffCanvas.parentNode.removeChild(diffCanvas);
    }

    var img1 = document.getElementById(baselineId);
    var img2 = document.getElementById(renderId);

    var width = img1.naturalWidth;
    var height = img1.naturalHeight;

    var canvasParent = document.getElementById('diffImageTd');
    var c = document.createElement('canvas');
    c.id = "imgsDifferenceCanvas";
    c.width = width;
    c.height = height;

    var ctx = c.getContext("2d");
    ctx.drawImage(img1, 0, 0);
    var imgData1 = ctx.getImageData(0, 0, width, height);
    ctx.drawImage(img2, 0, 0);
    var imgData2 = ctx.getImageData(0, 0, width, height);
    var diff = ctx.createImageData(width, height);

    pixelmatch(imgData1.data, imgData2.data, diff.data, width, height, {threshold: 0.1});

    ctx.putImageData(diff, 0, 0);

    imagesTable.style.display = "none";
    diffTable.style.display = "block";
    canvasParent.appendChild(c);
}