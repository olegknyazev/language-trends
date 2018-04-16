let colors = [
  ['#ff000080', '#ff000010'],
  ['#00ff0080', '#00ff0010'],
  ['#0000ff80', '#0000ff10']];

function initializeChart(element, data) {
  let datasets = [];
  for (let l = 0; l < data.langs.length; ++l)
    datasets.push({
        label: data.langs[l],
        borderColor: colors[l][0],
        backgroundColor: colors[l][1],
        fill: 'bottom',
        lineTension: 0,
        data: data.commits.map(r => r[1 + l])
      });
  let ctx = element.getContext('2d');
  let myChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.commits.map(r => new Date(r[0])),
      datasets: datasets
    },
    options: {
      legend: {
        position: 'right'
      },
      elements: {
        line: {
          borderWidth: 2
        },
        point: {
          radius: 0
        }
      },
      scales: {
        xAxes: [{
          type: 'time',
          time: {
            unit: 'year'
          }
        }]
      }
    }
  });
}
