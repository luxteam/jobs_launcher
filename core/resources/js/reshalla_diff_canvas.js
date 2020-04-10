function draw_reshalla_diff_canvas() {
    var diffCanvas = document.getElementById('diff');

    var baselineImg = document.getElementById('baselineimg');
    var renderedImg = document.getElementById('renderimg');

    diffCanvas.width = renderedImg.naturalWidth;
    diffCanvas.height = renderedImg.naturalHeight;

    var renderImgData = cv.imread(renderedImg);
    var baselineImgData = cv.imread(baselineImg);

    var renderImgDataProc = new cv.Mat();
    var baselineImgDataProc = new cv.Mat();

    cv.GaussianBlur(renderImgData, renderImgDataProc, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);
    cv.GaussianBlur(baselineImgData, baselineImgDataProc, new cv.Size(5, 5), 0, 0, cv.BORDER_DEFAULT);

    var imgDataDiff = Math.abs(renderImgDataProc.data - baselineImgDataProc.data);

//    cv.imshow(diffCanvas, diffImgData);
};