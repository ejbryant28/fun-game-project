function getData() {
	console.log("getting data");
	$.get('/progress-chart', makeProgressChart);
}

getData();

function makeProgressChart(result) {
	let categories = Object.keys(result);
	let datamap = {};
	let j;
	for (j=0; j < categories.length; j++) {
		let i;
		let category = categories[j];
		let categoryarray = [];
		for (i = 0; i < result[category].length; i++) {
			categoryarray.push({'x': new Date(result[category][i][0]), 'y':result[category][i][1]});
			if (categoryarray.length == result[category].length) {
				datamap[category] = categoryarray
			}
		};
	};
	console.log('enthusiasm data is ', datamap['enthusiasm']);

	let ctx = document.getElementById('progressChart').getContext('2d');

	let chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'scatter',

    // The data for our dataset
    data: {
        labels: 'times',
        datasets: [
        {
            label: "enthusiasm",
            pointBackgroundColor: 'rgb(212, 172, 13)',
            borderColor: 'rgb(212, 172, 13)',
            data: datamap['enthusiasm'],
            showLine: 'True',
            lineTension: 0.5,
            fill: 'False',
        },
        {
            label: "silliness",
            // pointBackgroundColor: 'rgb(100, 30, 22)',
            borderColor: 'rgb(100, 30, 22)',
            pointBorderColor: 'rgb(255, 255, 255)',
            data: datamap['silliness'],
            showLine: 'True',
            lineTension: 0.5,
            fill: 'False',

        },
        {
            label: "artistry",
            pointBackgroundColor: 'rgb(30, 132, 73)',
            borderColor: 'rgb(30, 132, 73)',
            data: datamap['artistry'],
            showLine: 'True',
            lineTension: 0.5,
            fill: 'False',

        },
        {
            label: "originality",
            pointBackgroundColor: 'rgb(175, 96, 26)',
            borderColor: 'rgb(175, 96, 26)',
            data: datamap['originality'],
            showLine: 'True',
            fill: 'False',

        },
        {
            label: "social",
            pointBackgroundColor: 'rgb(27, 79, 114)',
            borderColor: 'rgb(27, 79, 114)',
            data: datamap['social'],
            showLine: 'True',
            lineTension: 0.5,
            fill: 'False',

        },
        {
            label: "completion",
            pointBackgroundColor: 'rgb(74, 35, 90)',
            borderColor: 'rgb(74, 35, 90)',
            data: datamap['completion'],
            showLine: 'True',
            lineTension: 0.5,
            fill: 'False',

        }
        ]
    },

    // Configuration options go here
    options: {}
});
}