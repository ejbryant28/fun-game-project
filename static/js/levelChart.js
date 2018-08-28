
getData();

function getData() {
	$.get('/point-chart', makeChart);
}


function makeChart(result){
	// console.log(result)
	let chartLabels = Object.keys(result);
	// console.log(chartLabels)
	let finishedPointValues = [result[chartLabels[0]][0], result[chartLabels[1]][0], result[chartLabels[2]][0], result[chartLabels[3]][0], result[chartLabels[4]][0], result[chartLabels[5]][0]]
	// [result['originality'][0], result['silliness'][0], result['artistry'][0], result['completion'][0], result['enthusiasm'][0], result['social'][0]];
	// console.log(finishedPointValues)
	let unfinishedPointValues = [result[chartLabels[0]][1], result[chartLabels[1]][1], result[chartLabels[2]][1], result[chartLabels[3]][1], result[chartLabels[4]][1], result[chartLabels[5]][1]];
	// console.log(unfinishedPointValues)

	let ctx = document.getElementById('levelbarchart').getContext('2d');
	let chart = new Chart(ctx, {
	    // The type of chart we want to create
	    type: 'bar',

	    // The data for our dataset
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

	    // Configuration options go here
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