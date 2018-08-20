

function getPoints(test){
	let data = {
		"cat_vid_id" : test.id
	};
	$.post("/add_point", data, addPoint);
}
function addPoint(results) {
	let cat_vid_id = results["cat_vid_id"];
	let value = results['value'];
	let button_id = `#${cat_vid_id}`
	$(`${button_id}_score`).html(results['value']);
	$(button_id).prop("disabled", true);
}

function getButtons(button_id) {
	console.log(button_id)
	console.log(this)
	let data = {
		'button_id' : button_id
	};
	console.log(data)
	$.post("/check-point-given", data, disableButtons)
}

// function disableButtons(results) {
// 	alert('something')
// 	// console.log(results)
// 	// if (results) {
// 	// 	$.(results['button_id']).prop("disabled", true);
// 	// }
// }

function disableButtons(button_id) {
	$(button_id).prop("disabled", true);
}