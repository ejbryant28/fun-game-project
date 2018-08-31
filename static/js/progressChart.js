function getData() {
	console.log("getting data");
	$.get('/progress-chart', makeProgressChart);
}

getData();

function makeProgressChart(result) {
	let categories = Object.keys(result);
	let datamap = {};
	let j;
    let months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    // let months = Object.keys(monthMap);

	for (j=0; j < categories.length; j++) {
		let i;
		let category = categories[j];
		let categoryarray = [];
        // let monthMap = {'Jan':0, 'Feb':1, 'Mar':2, 'Apr':3, 'May':4, 'Jun':5, 'Jul':6, 'Aug':7, 'Sep':8, 'Oct':9, 'Nov':10, 'Dec':1}
		for (i = 0; i < result[category].length; i++) {
			// categoryarray.push({'x': new Date(result[category][i][0]), 'y':result[category][i][1]});
            // let date = new Date(year, monthIndex [, day [, hours [, minutes [, seconds [, milliseconds]]]]])
            // categoryarray.push({'x': date(result[category][i][0]), 'y':result[category][i][1]});
            let dateAr = result[category][i][0].split(' ');
            // console.log(dateAr)
            let time = dateAr[4].split(':');
            // console.log(time)
            // console.log(typeof(dateAr))
            // console.log(date_ar)
            // let test = parseInt(dateAr[3])
            // console.log(test)
            // console.log(typeof(test))
            // let month = monthMap[dateAr[2]];
            // console.log('month n is', month)
            monthIndex = months.indexOf(dateAr[2])
            let parsedDate = new Date( parseInt(dateAr[3]), monthIndex, parseInt(dateAr[1]), parseInt(time[0]), parseInt(time[1]), parseInt(time[2]))
            categoryarray.push({'x': parsedDate, 'y':result[category][i][1]});
            // categoryarray.push({'x': result[category][i][0], 'y':result[category][i][1]});
            console.log(categoryarray)

            // console.log(parsedDate)

			if (categoryarray.length == result[category].length) {
				datamap[category] = categoryarray
			}
		};
	};
	// console.log('enthusiasm data is ', datamap['enthusiasm']);

	let ctx = document.getElementById('progressChart').getContext('2d');

	let chart = new Chart(ctx, {
    // The type of chart we want to create
    type: 'scatter',

    // The data for our dataset
    data: {
        labels: months,
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
    options: {
            scales: {
                xAxes: [{
                    ticks: {
                        // Include a dollar sign in the ticks
                        callback: function(value, index, values) {
                            console.log(value, index, values)
                            return months[index]
                        }

                    }
                }]
            }
        }
    }
    )
}
    