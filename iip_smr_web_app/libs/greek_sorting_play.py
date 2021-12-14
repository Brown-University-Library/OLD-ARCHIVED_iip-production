"""
Resources:
- <https://www.py4u.net/discuss/10187>
- <https://www.programcreek.com/python/example/4364/unicodedata.combining>
- <https://en.wikipedia.org/wiki/Unicode_equivalence>
"""

import pprint, unicodedata
from operator import itemgetter

## source list ----------------------------------
initial_greek_word_list = [
    'ὧδε',
    'ἥμος',
    'ἃμα',
    'ἀβάβη',
    'ὥσπερ',
    'έρισα',
    'ί',
    'ἐπί',
    'ἵνδω',
    'ἠλίας',
    'ἒνθα',
    'ἡαρίβος',
    'ὠσείς',
    'ἲησοῦς',
    'α', 
    ]
print( f'initial_greek_word_list, ``{initial_greek_word_list}``' )
# simplistically_sorted = sorted( initial_greek_word_list )

## build no-diactritics -------------------------
''' Below is a line: ```nfkd_form = unicodedata.normalize('NFKD', entry)```.
    Printing the decomposed "normalized-form" of the word _looks_ the same as the original greek word, but is not.
    Instead, the character, and it's one-or-more diacritics have been broken out into separate entities. 
    The example below illustrates this.
    >>> 
    >>> import unicodedata
    >>> 
    >>> greek_word = 'ἃμα'
    >>> 
    >>> greek_word
    'ἃμα'
    >>> 
    >>> len(greek_word)
    3
    >>> 
    >>> print( f'1st original-character, ``{greek_word[0]}``; 2nd original-character, ``{greek_word[1]}``; 3rd original-character, ``{greek_word[2]}`` ' )
    1st original-character, ``ἃ``; 2nd original-character, ``μ``; 3rd original-character, ``α`` 
    >>> 
    >>> decomposed_word = unicodedata.normalize('NFKD', greek_word)
    >>> 
    >>> decomposed_word
    'ἃμα'
    >>> 
    >>> len( decomposed_word )
    5
    >>> 
    >>> print( f'1st decomposed-character, ``{decomposed_word[0]}``; 2nd decomposed-character, ``{decomposed_word[1]}``; 3rd decomposed-character, ``{decomposed_word[2]}``' )
    1st decomposed-character, ``α``; 2nd decomposed-character, ``̔``; 3rd decomposed-character, ``̀``
    >>> 

    Also below is the code: ```... if not unicodedata.combining(c)```, when building the no_diacritics version of the word.
    Diacritics have a 'combining class'. So this code creates the no_diacritics version of the word by looping through the denormalized characters, and ignoring ones that are diacritics.
'''
dct_list = []
for entry in initial_greek_word_list:
    print( f'\nentry, ``{entry}``' )
    # print( f'first-entry-character, ``{entry[0]}``' )
    nfkd_form = unicodedata.normalize('NFKD', entry)
    # print( f'nfkd_form, ``{nfkd_form}``' )
    # print( f'first-nfkd-character, ``{nfkd_form[0]}``' )
    assert type(nfkd_form) == str  
    no_diacritics = ''.join( [c for c in nfkd_form if not unicodedata.combining(c)] )
    print( f'no_diacritics, ``{no_diacritics}``' )
    data_dct = {
        'word_original': entry,
        'word_no_diacritics': no_diacritics,
        'first_character_original': entry[0],
        'first_character_no_diacritics': no_diacritics[0],
    }
    dct_list.append( data_dct )
print( f'dct_list, ``{pprint.pformat(dct_list)}``' )

## sort no-diacritics ---------------------------
normalized_sorted_greek_word_list = sorted( dct_list, key=itemgetter('word_no_diacritics') )
assert type(normalized_sorted_greek_word_list[0]) == dict
# print( f'normalized_sorted_greek_word_list, ``{pprint.pformat(normalized_sorted_greek_word_list)}``' )
final_sorted = []
for dct in normalized_sorted_greek_word_list:
    final_sorted.append( dct['word_original'] )
print( f'initial_greek_word_list, ``{initial_greek_word_list}``' )
# print( f'simplistically_sorted, ``{simplistically_sorted}``' )
print( f'final_sorted, ``{final_sorted}``' )

## final letter/linkage dct --------------------
results = {}
for normalized_dct in normalized_sorted_greek_word_list:
    assert type( normalized_dct ) == dict
    potential_key = normalized_dct['first_character_no_diacritics']
    print( f'potential_key, ``{potential_key}``' )
    if potential_key in results.keys():
        print( 'potential key already exists' )
        pass
    else:
        print( 'potential key new' )
        results[potential_key] = normalized_dct['word_original']
print( f'results, ``{pprint.pformat(results)}``' )

# coming