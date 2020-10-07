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
NEWBUFF = 3

KWIC_BUFF = 2

POSDICT = {"ADV": "adverb", "V": "verb", "N": "noun", "PREP": "preposition", "CC": "conjunction", "ADJ": "adjective"}
REVPOSDICT = {"noun": "N", "verb": "V", "adjective": "ADJ", "adverb": "ADV"}
MOODDICT = {"IND": "indicative", "PTC": "participle", "IMP": "imperative", "SUB": "subjunctive"}


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
			if line_count > 0 and len(row_word) > 0 and row_word[:1] != "?":
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

def get_latin_words_pos_new():

	with requests.Session() as s:
		download = s.get(settings_app.LATIN_CSV_NEW_URL)
		decoded = download.content.decode('utf-8')
		words = {}
		csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
		line_count = 0
		curtext = ""
		textrows = []
		for row in csv_reader:
			row_word = row[LATIN_LEMMA + NEWBUFF]
			if line_count > 0 and len(row_word) > 0 and row_word[:1] != "?":
				if curtext != row[LATIN_TEXT + NEWBUFF]:
					go_through_text_new(textrows, words)
					curtext = row[LATIN_TEXT + NEWBUFF]
					textrows = [row]
				else:
					textrows.append(row)
			line_count += 1
		go_through_text_new(textrows, words)
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
		latext = row[LATIN_TEXT]
		#getting pos info
		pos2 = getXML2POS(row[XML2])
		if pos2 is None:
			pos2 = getXML1POS(row[XML1], pos1, row[LATIN_POS2])
			if pos2 is None:
				pos2 = row[LATIN_POS2].lower()
				if pos2 == "":
					pos2 = "undefined"
			else:
				pos1 = pos2[0]
				pos2 = pos2[1]
				if pos1 in REVPOSDICT:
					pos1 = REVPOSDICT.get(pos1)
		else:
			pos1 = pos2[0]
			pos2 = pos2[1]
			if pos1 in REVPOSDICT:
					pos1 = REVPOSDICT.get(pos1)

		pos_string = row[LATIN_WORD]+ " (" + pos2 + ")"
		lemma_string = lemma + " " + pos1
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


def go_through_text_new(text_rows, words):
	row_len = len(text_rows)
	for x in range(0, row_len):
		row = text_rows[x]
		lemma = row[LATIN_LEMMA + NEWBUFF].lower()
		pos1 = row[LATIN_POS1 + NEWBUFF]
		latext = row[LATIN_TEXT + NEWBUFF]
		#getting pos info
		pos2 = getXML1POS(row[XML1 + NEWBUFF], pos1, row[LATIN_POS2 + NEWBUFF])
		if pos2 is None:
			pos2 = row[LATIN_POS2 + NEWBUFF].lower()
			if pos2 == "":
				pos2 = "undefined"
		else:
			pos1 = pos2[0]
			pos2 = pos2[1]
			if pos1 in REVPOSDICT:
				pos1 = REVPOSDICT.get(pos1)
		

		pos_string = row[LATIN_WORD + NEWBUFF]+ " (" + pos2 + ")"
		lemma_string = lemma + " " + pos1
		form = row[LATIN_WORD + NEWBUFF]
		KWICstr = ""
		for y in range(x - KWIC_BUFF, x + KWIC_BUFF + 1):
			if y >= 0 and y < row_len:
				KWICstr += " " + text_rows[y][LATIN_WORD + NEWBUFF]

		incp_id = row[LATIN_TEXT + NEWBUFF][:-4]
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


def getXML1POS(xmlString, pos, match):
	try:
		root = ET.ElementTree(ET.fromstring(xmlString)).getroot()
		first = None
		for elem in root.findall("word/entry/infl"):
			if first is None:
				first = elem
			if checkMatch(elem, pos, match):
				return parseByPos(elem)
		if first is None:
			return None
		else:
			return parseByPos(first)
	except Exception as e:
		#print(e) 
		return None

def checkMatch(el, pos, match):
	if el.find('pofs') is not None and el.find('pofs').text == POSDICT[pos]:
		if pos == "N":
			return el.find('case') is not None and match.lower() == el.find('case').text[:3]
		if pos == "V":
			return el.find('mood') is not None and MOODDICT[match] == el.find('mood').text
		if pos == "ADJ":
			return (el.find('case') is not None and match.lower() == el.find('case').text[:3]) \
			or (el.find('comp') is not None and match.lower() == el.find('comp').text[:3])
		return False
	else:
		return False


def getXML2POS(xmlString):
	try:
		root = ET.ElementTree(ET.fromstring(xmlString)).getroot()
		if root.tag == "infl":
			return parseByPos(root)
		for elem in root.findall("infl"):
			return parseByPos(elem)
	except Exception as e: 
		return None

def parseByPos(el):
	pos = el.find('pofs').text
	if pos == "noun":
		return (pos, pPart(el, "decl") + pPart(el, "case") + pPart(el, "gend") + pPart(el, "num"))
	elif pos == "verb":
		return (pos, pPart(el, "pers") + pPart(el, "num") + pPart(el, "voice") + pPart(el, "tense") + pPart(el, "mood")) 
	elif pos == "adjective":
		return (pos, pPart(el, "decl") + pPart(el, "case") + pPart(el, "gend") + pPart(el, "num") + pPart(el, "comp"))
	elif pos == "pronoun":
		return (pos, pPart(el, "case") + pPart(el, "gend") + pPart(el, "num"))
	else:
		return None


def pPart(elem, part):
	if elem.find(part) is None:
		return ""
	else:
		str = elem.find(part).text + " "
		if part == "num":
			str = str[:1]
		return str


def findMatch():
	with requests.Session() as s:
		download = s.get(settings_app.LATIN_CSV_URL)
		decoded = download.content.decode('utf-8')
		csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
		line_count = 1
		curtext = ""
		textrows = []
		for row in csv_reader:
			if line_count == 5:
				xmlString = row[XML1]
				pos = row[LATIN_POS1]
				match = row[LATIN_POS2]
				try:
					root = ET.ElementTree(ET.fromstring(xmlString)).getroot()
					first = None
					for elem in root.findall("word/entry/infl"):
						if first is None:
							first = elem
						if checkMatch(elem, pos, match):
							print(parseByPos(elem))
					if first is None:
						print("")
					else:
						print(parseByPos(first))
				except Exception as e:
						print(e) 
			line_count += 1

def formatNPOS(posdic):
	return ""

def formatVPOS(posdic):
	return ""
				
