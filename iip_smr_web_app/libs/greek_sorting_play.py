"""
Resources:
- <https://ianwscott.blog/2015/04/30/python-programming-proper-alphabetical-sorting-for-polytonic-greek/>
- <https://stackoverflow.com/a/62899722>
"""

import unicodedata

initial_greek_word_list = [
    'aiαι',
    'eιρύσ',
    'άδκα',
    'άλλω',
    'άνιος',
    'έρισα',
    'α',
    'αής',
    'αβαθιστα'
    ]

subsequent_list = []

d = {ord('\N{COMBINING ACUTE ACCENT}'): None}
print( f'd, ``{d}``' )

for entry in initial_greek_word_list:
    new_entry = unicodedata.normalize( 'NFD', entry ).translate( d )
    subsequent_list.append( new_entry )

print( f'subsequent_list, ``{pprint.pformat(subsequent_list)}``' )
