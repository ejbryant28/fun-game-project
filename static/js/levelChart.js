
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
	            backgroundColor: ['rgb(214, 136, 38)', 'rgb(55, 125, 168)', 'rgb(196, 43, 81)', 'rgb(149, 127, 189)', 'rgb(93, 205, 220)', 'rgb(44, 119, 108)'],
	            borderColor: ['rgb(214, 136, 38)', 'rgb(55, 125, 168)', 'rgb(196, 43, 81)', 'rgb(149, 127, 189)', 'rgb(93, 205, 220)', 'rgb(44, 119, 108)'],
	            data: finishedPointValues,
	        },

	        {
	            label: "In progress",
	            backgroundColor: ['rgba(214, 136, 38, .5)', 'rgba(55, 125, 168, .5)', 'rgba(196, 43, 81, .5)', 'rgba(149, 127, 189, .5)', 'rgb(93, 205, 220, .5)', 'rgba(44, 119, 108, .5)',],
	            borderColor: ['rgba(214, 136, 38, .5)', 'rgba(26, 82, 118, .5)', 'rgba(196, 43, 81, .5)', 'rgba(149, 127, 189, .5)', 'rgb(93, 205, 220, .5)', 'rgba(44, 119, 108, .5)',],
	            data: unfinishedPointValues,
	        }]
	    },
	    options: {
	    // title: {
     //            display: true,
     //            text: 'Current Levels',
     //            fontSize: 20,
     //            fontStyle: 'bold'
     //        },
        scales: {

            xAxes: [{
                stacked: true,
                
               	scaleLabel: {
                        display: true,
                        labelString:'Category',
                        fontSize: 20,
                    },
            }],
            yAxes: [{
                stacked: true,

                scaleLabel: {
                        display: true,
                        labelString:'Level',
                        fontSize: 20,
                    },
            }]
        }
    }
	});
	}