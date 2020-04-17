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

    var imgDataDiffProc = new cv.Mat();
    cv.absdiff(baselineImgDataProc, renderImgDataProc, imgDataDiffProc);

    var median = new cv.Mat();
    cv.medianBlur(imgDataDiffProc, median, 9);

    var kernel = cv.getStructuringElement(1, new cv.Size(5, 5), new cv.Point(2, 2));
    cv.morphologyEx(median, median, cv.MORPH_CLOSE, kernel);

    cv.cvtColor(median, median, cv.COLOR_BGR2GRAY);
    cv.threshold(median, median, 10, 255, cv.THRESH_BINARY);

    cv.imshow(diffCanvas, median);
};