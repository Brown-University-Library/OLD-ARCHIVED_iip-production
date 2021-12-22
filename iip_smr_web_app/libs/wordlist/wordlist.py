import collections
import csv
import logging
import pprint
import os
import unicodedata
from collections import OrderedDict
from operator import itemgetter

import requests
import xml.etree.ElementTree as ET
from iip_smr_web_app import settings_app


log = logging.getLogger(__name__)


LATIN_TEXT = 0
LATIN_WORDNUM = 1
LATIN_NUMBER = 6
LATIN_WORD = 7
LATIN_POS1 = 8
LATIN_POS2 = 9
LATIN_LEMMA = 10
XML1 = 11
XML2 = 12
NEWBUFF = 3

KWIC_BUFF = 2

POSDICT = {"ADV": "adverb", "V": "verb", "N": "noun", "PREP": "preposition", "CC": "conjunction", "ADJ": "adjective"}

#REVPOSDICT = {"noun": "N", "verb": "V", "adjective": "ADJ", "adverb": "ADV"}
REVPOSDICT = {v: k for k, v in POSDICT.items()}
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


def get_latin_words_pos_new():
    """
    Parse the Latin word list csv into a
    """
    log.debug( 'start' )

    with requests.Session() as s:
        log.debug( f'LATIN_CSV_NEW_URL, ``{settings_app.LATIN_CSV_NEW_URL}``' )
        download = s.get(settings_app.LATIN_CSV_NEW_URL)
        log.debug( f'download, ``{download}``' )
        decoded = download.content.decode('utf-8')
        words = {}
        csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
        line_count = 0
        curtext = ""
        textrows = []
        dbwords = []
        for row in csv_reader:
            log.debug( f'row, ``{row}``' )
            row_word = row[LATIN_LEMMA + NEWBUFF]
            if line_count > 0 and len(row_word) > 0 and row_word[:1] != "?":
                if curtext != row[LATIN_TEXT + NEWBUFF]:
                    go_through_text_new(textrows, words, dbwords)
                    curtext = row[LATIN_TEXT + NEWBUFF]
                    textrows = [row]
                else:
                    textrows.append(row)
            line_count += 1
            ## TEMP (for debugging) -------------
            # if line_count > 10:
            #     break
            ## ----------------------------------
        log.debug( f'textrows, ``{textrows}``' )
        log.debug( f'dbwords before 2nd gothrough(), ``{dbwords}``' )
        go_through_text_new(textrows, words, dbwords)  # adds one list-entry to dbwords
        log.debug( f'dbwords after 2nd gothrough(), ``{dbwords}``' )
        sorted_words = {k: v for k, v in sorted(words.items(), key = lambda item: item)}
        mapped_db = map(lambda x: "\n".join(x), dbwords)
        return_data = {"lemmas": count_words(sorted_words), "db_list": "\n\n\n".join(mapped_db)}
        log.debug( f'lemmas dct, ``{pprint.pformat(return_data["lemmas"])}``' )
        log.debug( f'db_list dct, ``{pprint.pformat(return_data["db_list"])}``' )
        return return_data

    ## end def get_latin_words_pos_new()


def get_greek_words_pos():
    """
    Parse the Greek word list csv into json data.
    """
    log.debug( 'start' )

    with requests.Session() as s:
        log.debug( f'GREEK_CSV_NEW_URL, ``{settings_app.GREEK_CSV_NEW_URL}``' )
        download = s.get(settings_app.GREEK_CSV_NEW_URL)
        log.debug( f'download, ``{download}``' )
        decoded = download.content.decode('utf-8')
        words = {}
        csv_reader = csv.reader(decoded.splitlines(), delimiter=",")
        line_count = 0
        curtext = ""
        textrows = []
        dbwords = []
        for row in csv_reader:
            log.debug( f'row, ``{row}``' )
            row_word = row[LATIN_LEMMA + NEWBUFF]
            log.debug( f'row_word, ``{row_word}``' )
            if line_count > 0 and len(row_word) > 0 and row_word[:1] != "?":
                if curtext != row[LATIN_TEXT + NEWBUFF]:
                    go_through_text_new(textrows, words, dbwords)
                    curtext = row[LATIN_TEXT + NEWBUFF]
                    textrows = [row]
                else:
                    textrows.append(row)
            line_count += 1
            ## TEMP (for debugging) -------------
            # if line_count > 10:
            #     break
            ## ----------------------------------
        log.debug( f'textrows, ``{textrows}``' )
        log.debug( f'dbwords before 2nd gothrough(), ``{dbwords}``' )
        go_through_text_new(textrows, words, dbwords)  # adds one list-entry to dbwords
        log.debug( f'dbwords after 2nd gothrough(), ``{dbwords}``' )
        
        sorted_words = {k: v for k, v in sorted(words.items(), key = lambda item: item)}
        log.debug( f'initial sorted_words, ``{sorted_words}``' )

        ## improve sorted_words -----------------
        assert type(words) == dict
        log.debug( f'initial words, ``{words}``' )
        words_key_list = list( words.keys() )
        assert type(words_key_list) == list
        log.debug( f'words_key_list, ``{pprint.pformat(words_key_list)}``' )
        normalized_key_ordered_dct = OrderedDict( [] )
        for word in words_key_list:
            nfkd_form = unicodedata.normalize('NFKD', word)
            no_diacritics = ''.join( [c for c in nfkd_form if not unicodedata.combining(c)] )
            normalized_key_ordered_dct[word] = no_diacritics
        log.debug( f'normalized_key_ordered_dct, ``{pprint.pformat(normalized_key_ordered_dct)}``' )

        sorted_x = sorted( normalized_key_ordered_dct.items(), key=itemgetter(1) )
        assert type(sorted_x) == list
        # log.debug( f'type(sorted_x), ``{type(sorted_x)}``' )
        log.debug( f'sorted_x, ``{sorted_x}``' )
        assert type(sorted_x[0]) == tuple
        sorted_normalized_key_ordered_dct = OrderedDict( sorted_x )
        log.debug( f'type(sorted_normalized_key_ordered_dct), ``{type(sorted_normalized_key_ordered_dct)}``' )
        assert type(sorted_normalized_key_ordered_dct) == collections.OrderedDict

        better_sorted_words_dct = collections.OrderedDict( [] )
        for word in sorted_normalized_key_ordered_dct.keys():
            better_sorted_words_dct[word] = words[word]
        log.debug( f'better_sorted_words_dct, ``{pprint.pformat(better_sorted_words_dct)}``' )

        sorted_words = better_sorted_words_dct

        mapped_db = map(lambda x: "\n".join(x), dbwords)
        return_data = {"lemmas": count_words(sorted_words), "db_list": "\n\n\n".join(mapped_db)}
        log.debug( f'lemmas dct, ``{pprint.pformat(return_data["lemmas"])}``' )
        
        lemmas_lst = []
        for lemma_dct in return_data['lemmas']:
            assert type(lemma_dct) == dict
            log.debug( f'lemma_dct, ``{lemma_dct}``' )
            lemma = lemma_dct['lemma']
            assert type( lemma ) == str
            if lemma not in lemmas_lst:
                lemmas_lst.append( lemma )
        key_lemma_ordered_dct = make_key_lemma_dct( lemmas_lst )
        return_data['key_lemma_ordered_dct'] = key_lemma_ordered_dct
                
        log.debug( f'return_data, ``{pprint.pformat(return_data)}``' )
        return return_data

    ## end def get_greek_words_pos()


def sort_greek_words( words_lst ):
    """ Runs the normal-form, non-diacritic sort.
        Returns back sorted list of original words. 
        Note: this function is not actually used!
        - Possible TODO: refactor wordlist.make_key_lemma_dct() to use the sort_greek_words() function.
        - For now, this function -- and it's test -- serve to illustrate a method for performing the sort -- which is used in make_key_lemma_dct(). """
    assert type(words_lst) == list
    normalized_word_dct_lst = []
    for word in words_lst:
        nfkd_form = unicodedata.normalize('NFKD', word)
        assert type(nfkd_form) == str  
        no_diacritics = ''.join( [c for c in nfkd_form if not unicodedata.combining(c)] )
        normalized_word_dct = {
            'original': word,
            'no_diacritics': no_diacritics,
        }
        normalized_word_dct_lst.append( normalized_word_dct )
    log.debug( f'normalized_word_dct_lst, ``{normalized_word_dct_lst}``' )
    ## sort no-diacritics ----------------------------
    normalized_sorted_word_dct_lst = sorted( normalized_word_dct_lst, key=itemgetter('no_diacritics') )
    assert type( normalized_sorted_word_dct_lst ) == list
    log.debug( f'normalized_sorted_greek_word_list, ``{normalized_sorted_word_dct_lst}``' )
    sorted_words = []
    for normalized_word_dct in normalized_sorted_word_dct_lst:
        sorted_words.append( normalized_word_dct['original'] )
    log.debug( f'sorted_words, ``{pprint.pformat(sorted_words)}``' )
    return sorted_words


def make_key_lemma_dct( lemmas_lst ):
    """ Converts list of lemmas into an ordered-dict where the key is an initial non-diacritic letter, and the value is the first matching lemma.
        Return brief example ``OrderedDict([('α', 'α'), ('ε', 'ἒνθα'), ('η', 'ἡαρίβος'), ('ι', 'ί'), ('ω', 'ὧδε')])``
        Called by get_greek_words_pos() """
    assert type(lemmas_lst) == list
    log.debug( 'starting make_key_lemma_dct()' )
    log.debug( f'lemmas_lst, ``{lemmas_lst}``' )
    ## build no-diactritics --------------------------
    normalized_lemma_list = []
    for lemma in lemmas_lst:
        nfkd_form = unicodedata.normalize('NFKD', lemma)
        assert type(nfkd_form) == str  
        no_diacritics = ''.join( [c for c in nfkd_form if not unicodedata.combining(c)] )
        normalized_lemma_dct = {
            'lemma_original': lemma,
            'lemma_no_diacritics': no_diacritics,
            'first_character_original': lemma[0],
            'first_character_no_diacritics': no_diacritics[0],
        }
        normalized_lemma_list.append( normalized_lemma_dct )
    log.debug( f'normalized_lemma_list, ``{normalized_lemma_list}``' )
    ## sort no-diacritics ----------------------------
    normalized_sorted_greek_word_list = sorted( normalized_lemma_list, key=itemgetter('lemma_no_diacritics') )
    ## final letter/linkage ordered-dict -------------
    results_ordered_dct = OrderedDict( [] )
    for normalized_dct in normalized_sorted_greek_word_list:
        potential_key = normalized_dct['first_character_no_diacritics']
        log.debug( f'potential_key, ``{potential_key}``')
        if potential_key in results_ordered_dct.keys():
            log.debug( 'potential_key WAS in keys()' )
            pass
        else:
            log.debug( 'potential_key was NOT in keys()' )
            results_ordered_dct[potential_key] = normalized_dct['lemma_original']
    log.debug( f'results_ordered_dct, ``{results_ordered_dct}``' )
    return results_ordered_dct

    ## end def make_key_lemma_dct()  


def make_alphabet_list( sorted_words ):
    alph_lst = []
    for (i, entry) in enumerate(sorted_words):
        log.debug( f'entry, ``{entry}``; i, ``{i}``' )
        if i > 20:
            break

    ## from <https://stackoverflow.com/a/62899722>
    initial_sorted_words = sorted_words
    resulting_sorted_words = []
    import unicodedata as ud
    for (i, entry) in enumerate(initial_sorted_words):
        log.debug( f'initial-entry, ``{entry}``; i, ``{i}``' )
        d = {ord('\N{COMBINING ACUTE ACCENT}'):None}  # "The d translation table lists Unicode ordinal translations...in this case, deleting the diacritic."
        # new_entry = ud.normalize('NFD', entry).upper().translate(d)
        new_entry = ud.normalize('NFD', entry).translate(d)
        log.debug( f'subsequent-entry, ``{new_entry}``; i, ``{i}``' )
        if i > 20:
            break
    return alph_lst




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


def go_through_text_new(text_rows, words, dbwords):
    dbwordlist = []
    row_len = len(text_rows)

    for x in range(0, row_len):
        row = text_rows[x]

        lemma = row[LATIN_LEMMA + NEWBUFF].lower()
        if lemma.find("|") > -1:
            lemma = lemma.replace("|", " | ")

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

        #adding to doubletree list
        dbwordlist.append(row[LATIN_LEMMA + NEWBUFF].upper() + "/" + pos1)


        form = row[LATIN_WORD + NEWBUFF]
        KWICstr = ""
        for y in range(x - KWIC_BUFF, x + KWIC_BUFF + 1):
            if y >= 0 and y < row_len:
                KWICstr += " " + text_rows[y][LATIN_WORD + NEWBUFF]

        # incp_id = row[LATIN_TEXT + NEWBUFF][:-4]
        incp_id = row[LATIN_TEXT + NEWBUFF]  # we need the full inscription-id to build the link
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
    dbwords.append(dbwordlist)

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


# This does not seem to be called from anywhere. It's also the only reference to settings_app.LATIN_CSV_URL
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

