import csv
import os


def get_latin_words(num):
	with open('iip_smr_web_app/libs/wordlist/latin.csv') as csv_file:
		words = {}
		csv_reader = csv.reader(csv_file, delimiter=",")
		line_count = 0
		header = []
		for row in csv_reader:
			row_word = row[13]
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
				
