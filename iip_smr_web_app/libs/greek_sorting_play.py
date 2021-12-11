"""
Resources:
- <https://www.py4u.net/discuss/10187>

- <https://ianwscott.blog/2015/04/30/python-programming-proper-alphabetical-sorting-for-polytonic-greek/>
- <https://stackoverflow.com/a/62899722>
"""

import pprint, unicodedata

## source list ----------------------------------
initial_greek_word_list = [
    'aiαι',
    'eιρύσ',
    'άδκα',
    'ἀβάβη',
    'ἃμα',
    'έρισα',
    'ἒνθα',
    'ί' ,
    'ἲησοῦς',
    'α',
    ]
print( f'initial_greek_word_list, ``{pprint.pformat(initial_greek_word_list)}``' )

## dict -----------------------------------------
word_dct = {}
for entry in initial_greek_word_list:
    print( f'\nentry, ``{entry}``' )
    print( f'first-entry-character, ``{entry[0]}``' )
    nfkd_form = unicodedata.normalize('NFKD', entry)
    print( f'nfkd_form, ``{nfkd_form}``' )
    print( f'first-nfkd-character, ``{nfkd_form[0]}``' )
    assert type(nfkd_form) == str  
    no_diacritics = ''.join( [c for c in nfkd_form if not unicodedata.combining(c)] )
    print( f'no_diacritics, ``{no_diacritics}``' )
    data_dct = {
        'a__first_raw_character': entry[0],
        'b__first_nfkd_character': nfkd_form[0],
        'c__no_diacritics': no_diacritics
    }
    word_dct[entry] = data_dct

pprint.pprint( word_dct )




# subsequent_list = []

# d = {ord('\N{COMBINING ACUTE ACCENT}'): None}
# print( f'd, ``{d}``' )


# for entry in initial_greek_word_list:
#     # new_entry = unicodedata.normalize( 'NFD', entry ).translate( d )
#     new_entry = unicodedata.normalize( 'NFD', entry )
#     subsequent_list.append( new_entry )
# print( f'subsequent_list, ``{pprint.pformat(subsequent_list)}``' )

# sorted_subseuent_list = sorted( subsequent_list )
# print( f'sorted_subseuent_list, ``{pprint.pformat(sorted_subseuent_list)}``' )


# def remove_accents( input_str ):
#     nfkd_form = unicodedata.normalize('NFKD', input_str)
#     return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
