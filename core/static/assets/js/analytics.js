const samples_by_type_data = JSON.parse(
  document.getElementById("samples_by_type").textContent
);
const samples_by_month_data = JSON.parse(
  document.getElementById("samples_by_month").textContent
);
const samples_by_study_data = JSON.parse(
    document.getElementById("samples_by_study").textContent
  );

function calculatePoint(i, intervalSize, colorRangeInfo) {
  var { colorStart, colorEnd, useEndAsStart } = colorRangeInfo;
  return useEndAsStart
    ? colorEnd - i * intervalSize
    : colorStart + i * intervalSize;
}

function interpolateColors(dataLength, colorScale, colorRangeInfo) {
  var { colorStart, colorEnd } = colorRangeInfo;
  var colorRange = colorEnd - colorStart;
  var intervalSize = colorRange / dataLength;
  var i, colorPoint;
  var colorArray = [];

  for (i = 0; i < dataLength; i++) {
    colorPoint = calculatePoint(i, intervalSize, colorRangeInfo);
    colorArray.push(colorScale(colorPoint));
  }

  return colorArray;
}

//Set the colours for the pie-chart here using D3 interpolate
const dataLength = samples_by_type_data.length;
const colorScale = d3.interpolateBlues; //options are interpolateInferno, interpolateMagma, interpolatePlasma, interpolateBlues
const colorRangeInfo = {
  colorStart: 0.5,
  colorEnd: 1,
  useEndAsStart: false,
};
var COLORS = interpolateColors(dataLength, colorScale, colorRangeInfo);

$(document).ready(function () {
  var ctx = document.getElementById("monthlysamples").getContext("2d");
  var chart = new Chart(ctx, {
    type: "line",
    // The data for our dataset
    data: {
      labels: samples_by_month_data.map((item) => item.sample_month_label),
      datasets: [
        {
          label: "Sample Count",
          fill: false,
          backgroundColor: "rgb(0,0,0,0)",
          borderColor: "rgb(48, 85, 187)",
          data: samples_by_month_data.map((item) => item.sample_count),
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        yAxes: [
          {
            ticks: {
              beginAtZero: true,
            },
            gridLines: {
              display: false,
            },
          },
        ],
        xAxes: [
          {
            gridLines: {
              display: false,
            },
          },
        ],
      },
      legend: {
        display: false,
      },
      layout: {
        padding: {
          left: 20,
          right: 40,
          top: 30,
          bottom: 10,
        },
      },
    },
  });

  const samples_by_type_chart_area = document.getElementById("samplestype").getContext("2d");
  const samples_by_type_chart = new Chart(samples_by_type_chart_area, {
    type: "doughnut",
    data: {
      datasets: [
        {
          backgroundColor: COLORS,
          data: samples_by_type_data.map((item) => item.sample_type_count),
        },
      ],
      labels: samples_by_type_data.map((item) => item.sample_type),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      legend: {
        position: "bottom",
      },
    },
  });


  const samples_by_study_chart_area = document.getElementById("samples_by_study_chart_area").getContext("2d");
  const samples_by_study_chart = new Chart(samples_by_study_chart_area, {
    type: "bar",
    data: {
      datasets: [
        {
          label: "Number of Samples",
          backgroundColor: COLORS,
          data: samples_by_study_data.map((item) => item.study_name_count),
        },
      ],
      labels: samples_by_study_data.map((item) => item.study_name),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      legend: {
        position: 'bottom',
      }
    },
  });
});
