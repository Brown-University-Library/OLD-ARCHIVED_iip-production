import csv
import os

LATIN_TEXT = 3
LATIN_WORDNUM = 4
LATIN_WORD = 10
LATIN_POS1 = 11
LATIN_POS2 = 12
LATIN_LEMMA = 13

KWIC_BUFF = 2


def get_latin_words_pos():
	with open('iip_smr_web_app/libs/wordlist/latin.csv') as csv_file:
		words = {}
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		header = []
		curtext = ""
		textrows = []
		for row in csv_reader:
			row_word = row[LATIN_LEMMA]
			if line_count != 0 and len(row_word) > 0 and row_word[:1] != "?":
				if curtext != row[LATIN_TEXT]:
					go_through_text(textrows, words)
					curtext = row[LATIN_TEXT]
					textrows = []
				textrows.append(row)

			if line_count == 0:
				header = row
			line_count += 1
		go_through_text(textrows, words)
		return {k: v for k, v in sorted(words.items(), key = lambda item: item)}

def go_through_text(text_rows, words):
	row_len = len(text_rows)
	for x in range(0, row_len):
		row = text_rows[x]
		lemma_string = row[LATIN_LEMMA] + " " + row[LATIN_POS1]
		pos2 = row[LATIN_POS2]
		if pos2 == "":
			pos2 = "undefined"
		pos_string = row[LATIN_WORD] + " " + pos2
		KWIC = ""
		for y in range(x - KWIC_BUFF, x + KWIC_BUFF):
			if y >= 0 and y < row_len:
				KWIC += " " + text_rows[y][LATIN_WORD]
		KWIC += " (" + row[LATIN_TEXT] + ")"
		if lemma_string in words:
			if pos_string in words[lemma_string]:
				words[lemma_string][pos_string].append(KWIC)
			else:
				words[lemma_string][pos_string] = [KWIC]
		else:
			words[lemma_string] = {pos_string: [KWIC]}

def get_latin_words(num):
	with open('iip_smr_web_app/libs/wordlist/latin.csv') as csv_file:
		words = {}
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		header = []
		for row in csv_reader:
			row_word = row[LATIN_LEMMA]
			if line_count < num and line_count != 0 and len(row_word) > 0 and row_word[:1] != "?":
				word = {}
				word["data"] = row[3][:-4] + ", line " + row[5] + " (" + row[7] + ")"
				word["link_id"] = row[3] + "" + row[4]
				if row_word in words:
					words[row_word].append(word)
				else:
					words[row_word] = [word]
			if line_count == 0:
				header = row
			line_count += 1
		return {k: v for k, v in sorted(words.items(), key = lambda item: item)}


def get_latin_word(latin_id):
	info = {}
	with open('iip_smr_web_app/libs/wordlist/latin.csv') as csv_file:
		header = []
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				header = row
			else:
				this_id = row[3] + "" + row[4]
				if this_id == latin_id:
					header_index = 3
					while header_index < len(header) - 1:
						info.update({header[header_index].replace(" ", "") : row[header_index]})
						header_index += 1
					return info
			line_count += 1
	return info

def get_latin_KWIC(latin_id, buf_num):
	kwic = ""

	index = latin_id.find(".xml") + 4
	inscrip = latin_id[:index]
	num = int(latin_id[index:])
	
	with open('iip_smr_web_app/libs/wordlist/latin.csv') as csv_file:
		finding = 0
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		for row in csv_reader:
			if line_count == 0:
				line_count += 1
				continue
			word_num = int(row[4])
			if row[3] == inscrip and word_num <= num + buf_num and word_num >= num - buf_num:
				word = row[7]
				kwic += word + " "
				finding = 1
			elif finding:
				return kwic[:len(kwic) - 1]
		
	if len(kwic) == 0:
		return "KWIC not found"
	else:
		return kwic[:len(kwic) - 1]

def getPOS(row):
	pos1 = row[11]
	pos2 = row[12]
	if pos1 == "N":
		print("noun")

	print(row)


				
