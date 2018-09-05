
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
	            // fill: false
	            backgroundColor: ['rgb(245, 236, 135)', 'rgb(26, 82, 118)', 'rgb(196, 43, 81)', 'rgb(149, 127, 189)', 'rgb(93, 173, 226)', 'rgb(44, 119, 108)'],
	            borderColor: ['rgb(245, 236, 135)', 'rgb(26, 82, 118)', 'rgb(196, 43, 81)', 'rgb(149, 127, 189)', 'rgb(93, 173, 226)', 'rgb(44, 119, 108)'],
	            data: finishedPointValues,
	        },

	        {
	            label: "In progress",
	            backgroundColor: 'rgba(245, 236, 135, .5)',
	            borderColor: 'rgb(209, 242, 235)',
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