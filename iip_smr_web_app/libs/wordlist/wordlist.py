import csv
import os
import requests
from iip_smr_web_app import settings_app
import xml.etree.ElementTree as ET

LATIN_TEXT = 0
LATIN_WORDNUM = 1
LATIN_WORD = 7
LATIN_POS1 = 8
LATIN_POS2 = 9
LATIN_LEMMA = 10
XML1 = 11
XML2 = 12

KWIC_BUFF = 2

POSDICT = {"ADV": "adverb", "V": "verb", "N": "noun", "PREP": "preposition", "CC": "conjunction", "ADJ": "adjective"}


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
	#with requests.Session() as s:
	with open('iip_smr_web_app/libs/wordlist/corrected_latin.csv') as csv_file:

		#download = s.get(settings_app.LATIN_CSV_URL)
		#decoded = download.content.decode('utf-8')
		csv_reader = csv.reader(csv_file, delimiter=",")
		words = {}
		#csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
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
				else:
					textrows.append(row)
			line_count += 1
		go_through_text(textrows, words)
		sorted_words = {k: v for k, v in sorted(words.items(), key = lambda item: item)}
		#findMatch()
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
		pos2 = getXMLPOS(row[XML2])
		if pos2 == "":
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
		KWIC = [KWICstr, incp_id]

		lemma_dict = words.get(lemma_string)
		if lemma_dict is not None:
			form_dict = lemma_dict.get("forms").get(pos_string)
			if form_dict is not None:
				form_dict.get("kwics").append(KWIC)
			else:
				form = {"form": form, "pos": pos2, "kwics": [KWIC]}
				lemma_dict["forms"][pos_string] = form
		else:
			forms = {"form": form, "pos": pos2, "kwics": [KWIC]}
			words[lemma_string] = {"lemma": lemma, "pos": pos1, "forms": {pos_string: forms} }


def getXMLPOS(xmlString):
	try:
		root = ET.ElementTree(ET.fromstring(xmlString)).getroot()
		if root.tag == "infl":
			return parseByPos(root)
		for elem in root.findall("infl"):
			return parseByPos(elem)
	except Exception as e: 
		print(e)
		return ""

def parseByPos(elem):
	print("5")
	pos = elem.find('pofs').text
	if pos == "noun":
		return elem.find("decl").text + " " + elem.find("case").text + " " + elem.find("gend").text + " " + elem.find("num").text[:1]
	elif pos == "verb":
		return elem.find("pers").text + " " + elem.find("num").text[:1] + " " + elem.find("voice").text + " " + elem.find("tense").text + " " + elem.find("mood").text;
	elif pos == "adjective":
		return elem.find("decl").text + " " + elem.find("case").text + " " + elem.find("gend").text + " " + elem.find("num").text[:1] + elem.find("comp").text
	elif pos == "pronoun":
		return elem.find("case").text + " " + elem.find("gend").text + " " + elem.find("num").text[:1]
	else:
		return ""


def findMatch():
	with open('iip_smr_web_app/libs/wordlist/corrected_latin.csv') as csv_file:
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		curtext = ""
		textrows = []
		for row in csv_reader:
			if line_count == 2:
				try:
					print("1")
					root = ET.ElementTree(ET.fromstring(row[XML2])).getroot()
					print("2")
					if root.tag == "infl":
						print("3")
						print(parseByPos(root))
						return
					for elem in root.findall("infl"):
						print("4")
						print(parseByPos(elem))
						return
				except Exception as e: 
					print(e)
					return
			line_count += 1

def formatNPOS(posdic):
	return ""

def formatVPOS(posdic):
	return ""
				
