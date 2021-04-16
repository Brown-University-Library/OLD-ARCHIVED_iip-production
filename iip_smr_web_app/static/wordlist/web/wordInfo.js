function create(elementType) {
	let newElement = document.createElement(elementType);
	for (let i = 1; i < arguments.length; i++) {
		let currentArgument = arguments[i];		
		if (typeof(currentArgument) === 'string') {
			newElement.innerHTML += currentArgument;
		} else if (Array.isArray(currentArgument)) {
			for (let j = 0; j < arguments[i].length; j++) {
				if (typeof(arguments[i][j]) === 'string') {
					newElement.innerHTML += currentArgument[j];		
				} else {	
					newElement.appendChild(currentArgument[j]);
				}
			}
		} else if (currentArgument instanceof Element) {
			newElement.appendChild(currentArgument);
		} else {
			Object.getOwnPropertyNames(currentArgument).forEach(
				function (val, idx, array) {
					newElement.setAttribute(val, currentArgument[val]);
				}
			);
		}
	}
	return newElement;
}

let table = document.getElementById("occurrences");
let xmlCells = document.getElementsByClassName("xml");
let tableRows = table.getElementsByTagName("tr");
for (let i = 0; i < tableRows.length; i++) {
	if (i % 2 == 0) {
		tableRows[i].hidden = "true";
	} else {
		let currentRow = tableRows[i];
		let nextRow = tableRows[i + 1];
		let expandButton = create("a", "▼", {class: "expand-button"});
		expandButton.addEventListener("click", () => {
			if (nextRow.hidden == true) { nextRow.hidden = false; } 
			else { nextRow.hidden = true; }
		}, false);
		currentRow.appendChild(create("td", [expandButton]));
	}
}

