import csv
import os
import requests
from iip_smr_web_app import settings_app

LATIN_TEXT = 3
LATIN_WORDNUM = 4
LATIN_WORD = 10
LATIN_POS1 = 11
LATIN_POS2 = 12
LATIN_LEMMA = 13

KWIC_BUFF = 2


# data is formatted as a list of dictionaries 
# each dictionary is a lemma
# LEMMA DICTIONARY FORMAT
# [ lemma: normalized form of word
#   pos: part of speech of lemma
#   count: # of times word appears in inscriptions
#   forms : dictionary of different forms of word]
# FORMS DICTIONARY FORMAT
# [ form: string of form
#   count: # of times form appears
#   pos: pos information about the form
#   kwics: list of duples of the form, first index is kwic, second is inscrp id]
# (kwics and inscription ids should correspond to each other)
def get_latin_words_pos():
	with requests.Session() as s:
		download = s.get(settings_app.LATIN_CSV_URL)
		decoded = download.content.decode('utf-8')
		words = {}
		csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
		line_count = 0
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
			line_count += 1
		go_through_text(textrows, words)
		sorted_words = {k: v for k, v in sorted(words.items(), key = lambda item: item)}
		return count_words(sorted_words)

def count_words(words):
	counted = []
	for lemma, lemma_dict in words.items():
		total = 0
		for form, form_dict in lemma_dict["forms"].items():
			formlen = len(form_dict["kwics"])
			total += formlen
			form_dict["count"] = formlen
		lemma_dict["count"] = total
		counted.append(lemma_dict)
	return counted


def go_through_text(text_rows, words):
	row_len = len(text_rows)
	for x in range(0, row_len):
		row = text_rows[x]
		lemma = row[LATIN_LEMMA].lower()
		pos1 = row[LATIN_POS1]
		lemma_string = lemma + " " + pos1
		pos2 = row[LATIN_POS2].lower()
		if pos2 == "":
			pos2 = "undefined"
		pos_string = row[LATIN_WORD]+ " (" + pos2 + ")"
		form = row[LATIN_WORD]
		KWICstr = ""
		for y in range(x - KWIC_BUFF, x + KWIC_BUFF + 1):
			if y >= 0 and y < row_len:
				KWICstr += " " + text_rows[y][LATIN_WORD]

		incp_id = row[LATIN_TEXT][:-4]
		if len(incp_id) < 3:
			print("boop")
		KWIC = [KWICstr, incp_id]

		lemma_dict = words.get(lemma_string)
		if lemma_dict is not None:
			form_dict = lemma_dict.get("forms").get(pos_string)
			if form_dict is not None:
				form_dict.append(KWIC)
			else:
				form = {"form": form, "pos": pos2, "kwics": [KWIC]}
				lemma_dict["forms"][pos_string] = form
		else:
			forms = {"form": form, "pos": pos2, "kwics": [KWIC]}
			words[lemma_string] = {"lemma": lemma, "pos": pos1, "forms": {pos_string: forms} }

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


				
