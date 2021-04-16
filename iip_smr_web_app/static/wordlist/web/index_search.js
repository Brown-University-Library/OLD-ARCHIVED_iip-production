// Utility Functions
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

// Return true if `element` is in `array`
function inArray(element, array) {
	return !(array.indexOf(element) == -1);
}

// Return the given string with all Greek diacritics removed.
function normalizeGreek(text) {
	return text.normalize('NFD').replace(/[\u0300-\u036f]/g, "");
}

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
}
function insertBefore(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode);
}

let controlsBar = create("div", {id: "controlsBar"}, [
	create("input", {
		type: "text", 
		placeholder: "Search for matching words...",
		id: "searchBar"
	}),
	create("label", "Region", {id: "regionLabel", for: "regionSelect"}),
	create("div", {class: "select-wrapper"}, [
		create("select", {id: "regionSelect"}, [
			create("option", "All", {value: "all"})
		]),
	]),
	create("label", "Sort by", {id: "sortByLabel", for: "sortSelect"}),
	create("div", {class: "select-wrapper"}, [
		create("select", {id: "sortSelect"}, [
			create("option", "Occurences", {value: "occurrences"}),
			create("option", "Alphabet", {value: "alphabet"})
		])
	]),
	create("input", {
		type: "checkbox", 
		id: "showSuspiciousCheck"
	}),
	create("label", "Show suspicious words", {
		id: "showSuspiciousLabel", for: "showSuspiciousCheck"
	}),
]);

// Add created elements to document
let words = document.getElementById("words");
words.parentNode.insertBefore(controlsBar, words);

// Create a searchbar
let searchbar = document.getElementById("searchBar");

// Create checkbox for toggling visibility of suspicious words
let showSuspiciousCheck = document.getElementById("showSuspiciousCheck");
showSuspiciousCheck.addEventListener("click", render, false);
let showSuspiciousLabel = document.getElementById("showSuspiciousLabel");

// Create a <select> for choosing sort method
let sortSelect = document.getElementById("sortSelect");
sortSelect.addEventListener("change", () => {
	sortWordList();
	render();
}, false);

let sortByLabel = document.getElementById("sortByLabel");

// Add regex explanation
let regexExplanation = `
	<h3>Regular Expressions</h3>
	<p>
	The search function in this application supports 
	<a href="https://en.wikipedia.org/wiki/Regular_expression">regular			
	expressions</a>. A regular expression, or "regex," is a text string that
	matches a set of possible strings according to a number of standardized
	syntactic rules. Regular expressions are an extremely powerful tool in
	text processing, and their usage cannot be fully explained here. However,
	we hope that the following examples will provide a useful grounding for use
	in this application.
	</p>
	<ul>
	<li>
	<code>^</code> represents the beginning of a string. For instance, 
	<code>^pre</code> will match any word that starts with "pre."
	</li>
	<li>
	<code>$</code> represents the end of a string. For instance, <code>us$</code>
	will match any word that ends in "us."
	</li>
	<li>
	<code>.*</code> matches any sequence of characters. For instance, 
	<code>au.*us</code> will match any word containing "au" followed by 
	anything, followed by "us." "augustus," "taurus," and "paulus" would 
	all be matched. 
	</li>
	<li>
	Brackets will match expressions with any one of the containing 
	characters. For instance, <code>gr[ea]y</code> will match "grey" and "gray."
	</li>
	<li>
	Parenthesis containing expressions seperated by the pipe character, "|" , 
	will match words containing any one of the pipe-seperated expressions. 
	For instance, <code>th(is|at)</code> will match "this" and "that". On 
	most qwerty keyboards, the pipe character appears above the enter key. 
	</li>
	<li>
	The above tools can all be combined. For instance, 
	<code>^([ui]n|ir).*able$</code> will match anything beginning with 
	"un" "in" or "ir" and ending with "able," such as "inviolable," 
	"incomparable," "unrecognizable," and "irresistable."
	</li>
	</ul>
`;
document.getElementById("all-wrapper").appendChild(create(
	"div", 
	{class: "info-box", 
	 style: "text-align: left; background: whitesmoke; padding: 10px; margin: 5px; border: 1px solid black;"}, 
	regexExplanation)
);


// Global Variables
let wordsPerPage = 60; 
let after = 0;
let wordList = []
let regionsSet = new Set();

function sortWordList() {
	after = 0;
	if (sortSelect.value == "occurrences") {
		wordList.sort((a, b) => {
			return b.getAttribute("data-num-occurrences") - 
			       a.getAttribute("data-num-occurrences");
		});
	} else if (sortSelect.value = "alphabet") {
		wordList.sort((a, b) => {
			return noAnnoyances(a.children[0].innerHTML).localeCompare(
				noAnnoyances(b.children[0].innerHTML)
			);
		});
	}
}
let annoyances = ["_", "-", ".", "`", "!", " ", "\n", "\t", "~", "ʹ", 
                  "῾", "῀", "‘", "῀", "᾽", "ʻ", "ʼ", "ʽ", "’", "‛",
                  "…", "∞", "○", "◦", "⚬", "￮", "¹", "½", "¾", "ɐ"]

function firstNonAnnoyance(s) {
	for (ch of s) { if (!annoyances.includes(ch)) { return ch; } }
}

function noAnnoyances(s) {
	let filtered = "";
	for (ch of s) {
		if (!annoyances.includes(ch)) { filtered += ch; }
	}
	return filtered;
}

function exists(x) {
	if (typeof(x) == "undefined"
	    || x == null
		|| x == ""
	) { return false; }
	return true;
}

for (let i = 0; i < wordsArray.length; i++) {
	wordsArray[i].text.replace(/[\x30\x29\x04]/g,"")
	                  .replace(/[\u00AD\u002D\u2011]+/g,'')
					  .replace(String.fromCharCode(173), "");
	if (wordsArray[i].text.length < 1 
	    || wordsArray[i].text[0] == null 
		|| typeof wordsArray[i].text != "string" 
		|| wordsArray[i].text.includes("\n") 
		|| wordsArray[i].text[0].charCodeAt(0) == 173 
		|| isNaN(wordsArray[i].text[0].charCodeAt(0))
		|| !exists(noAnnoyances(wordsArray[i].text)) 
	    //|| inArray(wordsArray[i].text[0], annoyances)
	) { continue; }
	if (wordsArray[i].regions != null) {
		for (let j = 0; j < wordsArray[i].regions.length; j++) {
			regionsSet.add(wordsArray[i].regions[j]);
		}
	}	
	let newWord = create("li", 
		{"data-num-occurrences": wordsArray[i].occurrences, 
		 "data-regions": wordsArray[i].regions},
		[create("a", wordsArray[i].text, 
		 {href: wordsArray[i].text + "_.html"})]
	);
	if (wordsArray[i].suspicious) { newWord.classList = "suspicious"; }
	wordList.push(newWord);
}

let regionSelect = document.getElementById("regionSelect");
let regionLabel = document.getElementById("regionLabel");
for (var i of regionsSet) {
	regionSelect.appendChild(create("option", i, {value: i}));
}

regionSelect.addEventListener("change", () => {
	render();
}, false);

let prev = document.createElement("button");
let next = document.createElement("button");
prev.innerHTML = "PREV"
next.innerHTML = "NEXT"
prev.id = "previous-button";
next.id = "next-button";

let alphabetSelect = create("div", {id: "alphabet-select"});

let bottomControls = create("div", {id: "bottomControls"}, [
	alphabetSelect, prev, next
]);

insertAfter(bottomControls, words);

function countSkipped(n) {
	let count = 0;
	for (let i = 0; i < n; i++) {
		if (checkSkip(wordList[i])) { count += 1; }
	}
	return count;
}

function countSkipped(start, end) {
	//console.log("Checking skip from " + start + " to " + end);
	let count = 0;
	for (let i = start; i < end; i++) {
		if (checkSkip(wordList[i])) { count += 1; }
	}
	return count;
}

function jumpToLetter(evt) {
	targetLetter = normalizeGreek(evt.target.innerHTML[0]);
	//console.log("targetLetter: " + targetLetter);
	sortSelect.value = "alphabet";
	sortWordList();
	let skipped = 0;
	for (let i = 0; i < wordList.length; i += wordsPerPage) {
		skipped += countSkipped(i, Math.min(i + wordsPerPage, 
		                                    wordList.length - 1));
		let firstWord = noAnnoyances(
			wordList[i + skipped].children[0].innerHTML
		);
		let lastWordIndex = Math.min(i + skipped + wordsPerPage - 1, 
		                             wordList.length - 1);
		let lastWord = noAnnoyances(
			wordList[lastWordIndex].children[0].innerHTML
		);
		//console.log(["Page " + i / wordsPerPage, 
		//             "First Word: " + firstWord,
		//             "Last Word: " + lastWord].join(", "));
		if (letter == null || typeof(letter) == 'undefined') {
			console.log("Letter is null.");
			continue;
		}
		if ((normalizeGreek(firstWord[0]) <= targetLetter  
		     && normalizeGreek(lastWord[0]) >= targetLetter)
			|| lastWordIndex > wordList.length
		) {
			//console.log("Target letter is in between '" 
			//            + firstWord[0] + "' and '" +
			//            lastWord[0] + "'. Jumping to page.")
			after = i; 
			render();
			return;
		}
	}
}

let letters = new Set();
for (let i = 0; i < wordList.length; i++) {
	letter = firstNonAnnoyance(wordList[i].children[0].innerHTML);
	if (letter != null && typeof letter != 'undefined') {
		letters.add(normalizeGreek(letter));
	}
}
sortedLetters = Array.from(letters).sort();
for (let i = 0; i < sortedLetters.length; i++) {
	let link = create("a", "" + sortedLetters[i]);
	link.addEventListener("click", jumpToLetter, false);
	alphabetSelect.appendChild(link);
}

prev.addEventListener("click", () => {
	after = Math.max(after - wordsPerPage, 0); 
	render();
}, false);
next.addEventListener("click", () => {
	after += wordsPerPage; 
	render();
}, false);

function checkSkip(word) {
	if (!showSuspiciousCheck.checked) {
		if (word.classList.contains("suspicious")) {return true;}
	}
	if (word.children[0].innerHTML.length < 1) {return true;}
	if (regionSelect.value != "all") {
		if (word.getAttribute("data-regions").
		    indexOf(regionSelect.value) == -1
		) {
			return true;
		}
	}
	return false;
}

let lastRender = 0;

let standardSort = true;
function render() {
	//let timeDif = Date.now() - lastRender;
	//if (timeDif < 500) {setTimeout(render, 500 - timeDif); return;}
	//lastRender = Date.now();
	while (words.firstChild) {
		words.removeChild(words.firstChild);
	}
	let normalizedSearch = normalizeGreek(searchbar.value);
	let re = new RegExp(normalizedSearch);
	if (searchbar.value != "") {
		standardSort = false;
		wordList.sort((a, b) => {
			a.text = normalizeGreek(a.children[0].innerHTML);
			b.text = normalizeGreek(b.children[0].innerHTML);	
			a.regexMatch = false;
			b.regexMatch = false;		
			if (a.text.match(re) != null) {
				a.regexMatch = true; 
			}
			if (b.text.match(re) != null) { b.regexMatch = true; }
			a.levEdit = Levenshtein.get(a.text, normalizedSearch);
			b.levEdit = Levenshtein.get(b.text, normalizedSearch)
			if (a.regexMatch && !b.regexMatch) { return -1;}
			if (b.regexMatch && !a.regexMatch) { return 1;}
			
			return a.levEdit - b.levEdit;
		});
	} else {
		if (!standardSort) {
			sortWordList();
			standardSort = true;
		}
	}
	let added = 0; let seen = 0;
	prev.disabled = true; next.disabled = true;
	
	for (let i = 0; i < wordList.length; i++) {
		if (added == wordsPerPage) {
			next.disabled = false;
			break;
		}
		let word = wordList[i]
		if (checkSkip(word)) {continue;}
		let text = word.children[0].innerHTML.toLowerCase();
		let searchText = searchbar.value.toLowerCase();
		if (text.startsWith(searchText) || 
		    wordList[i].levEdit < 4 ||
		    wordList[i].regexMatch) {
			seen += 1;
			if (seen > after) {
				added += 1;
				words.appendChild(word)
			}
		}
	}
	if (after > 0) {
		prev.disabled = false;
	}
}

var renderTimeout;

searchbar.addEventListener("input", () => {
	clearTimeout(renderTimeout);
	renderTimeout = setTimeout(function() {
		after = 0;
		render();
	}, 150);
}, false);
sortWordList();
render();

// Fix the uneven edges on github pages.
if (window.location.href.includes("github.io")) {
	document.styleSheets[0].insertRule(".info-box {max-width: 993px;}");
}
