function showImagesSubtraction(baselineId, renderId, resultCanvasId) {
//    create popup
    var c = document.getElementById(resultCanvasId);
    var ctx = c.getContext("2d");

    var img1 = document.getElementById(baselineId);

    var width = img1.width;
    var height = img1.height;

    ctx.drawImage(img1, 0, 0);
    var imgData1 = ctx.getImageData(0, 0, width, height);

    var img2 = document.getElementById(renderId);
    ctx2.drawImage(img2, 0, 0);
    var imgData2 = ctx2.getImageData(0, 0, width, height);

    var ctx = c.getContext("2d");
    var diff = ctx.createImageData(width, height);

    pixelmatch(imgData1.data, imgData2.data, diff.data, width, height, {threshold: 0.1});

    ctx.putImageData(diff, 0, 0);
}