
function getData() {
	$.get('/point-chart', makeChart);
}

getData();

function makeChart(result){
	let chartLabels = Object.keys(result);
	let finishedPointValues = [result[chartLabels[0]][0], result[chartLabels[1]][0], result[chartLabels[2]][0], result[chartLabels[3]][0], result[chartLabels[4]][0], result[chartLabels[5]][0]];
	let unfinishedPointValues = [result[chartLabels[0]][1], result[chartLabels[1]][1], result[chartLabels[2]][1], result[chartLabels[3]][1], result[chartLabels[4]][1], result[chartLabels[5]][1]];
	let ctx = document.getElementById('levelbarchart').getContext('2d');
	let chart = new Chart(ctx, {
	    type: 'bar',
	    data: {
	        labels: chartLabels,
	        datasets: [{
	            label: "Completed Levels",
	            backgroundColor: 'rgb(52, 73, 94)',
	            borderColor: 'rgb(52, 73, 94)',
	            data: finishedPointValues,
	        },

	        {
	            label: "In progress",
	            backgroundColor: 'rgb(83, 189, 184)',
	            borderColor: 'rgb(83, 189, 184)',
	            data: unfinishedPointValues,
	        }]
	    },
	    options: {
        scales: {
            xAxes: [{
                stacked: true
            }],
            yAxes: [{
                stacked: true
            }]
        }
    }
	});
	}