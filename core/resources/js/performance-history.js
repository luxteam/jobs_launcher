var performanceCharts = {}
var colors = ['#82438CFF', '#327A5BFF', '#F4B400FF', '#2D538FFF', '#DB4437FF', '#4285F4FF', '#E8E541FF', '#24C959FF', '#00ACC1FF', '#FF7043FF']

function changeMetric(id, metric) {
    performanceCharts[id].chart.data.labels = performanceCharts[id].renderData[metric].labels
    performanceCharts[id].chart.data.datasets = performanceCharts[id].renderData[metric].datasets
    performanceCharts[id].chart.options = performanceCharts[id].optionsData[metric]
    performanceCharts[id].chart.update()
}