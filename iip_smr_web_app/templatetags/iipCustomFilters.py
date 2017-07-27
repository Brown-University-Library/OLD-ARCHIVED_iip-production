from django import template
from django.template.defaultfilters import stringfilter
import re
from iip_smr_web_app import forms
import requests
import xml.etree.ElementTree as ET


register = template.Library()

@register.filter(name='underscoreToSpace')
@stringfilter
def underscoreToSpace(value):
    return value.replace("_", " ")

@register.filter(name='cleanDates')
@stringfilter
def cleanDates(value):
    value = re.sub(r'-(\d+)', r' \1 BCE', value)
    value = re.sub(r'(\d+)\b(?!\sBCE)', r' \1 CE', value)
    return value

vocab_request = requests.get("http://cds.library.brown.edu/projects/iip/include_taxonomies.xml")
vocab = ET.fromstring(vocab_request.content)
vocab_dict = {
    "grc":"Greek",
    "he":"Hebrew",
    "la":"Latin",
    "arc":"Aramaic",
    "x-unknown":"Unknown",
}
for tax in vocab.findall('{http://www.tei-c.org/ns/1.0}taxonomy'):
    for e in tax.findall('{http://www.tei-c.org/ns/1.0}category'):
        name = e.attrib['{http://www.w3.org/XML/1998/namespace}id']
        value = e.find('{http://www.tei-c.org/ns/1.0}catDesc').text
        vocab_dict[name] = value

@register.filter(name='tax')
def tax(value):
    return vocab_dict[value] if value in vocab_dict else value

@register.filter(name='vocabSort')
def vocabSort(values):
    return sorted(values, key=lambda x: tax(x[0]).lower())


@register.filter(name='indexList')
def indexList(sequence, position):
    return sequence[position]



@register.filter(name='languageClean')
def languageClean(language):
    language_cleaned = [];
    for l in language:
        language_cleaned.append(l.encode('utf-8'))
    return language_cleaned




@register.filter(name='placeClean')
def placeClean(place):
    # place_cleaned = [];
    # for c in place:
    #     if c == ']':
    #         place_cleaned.append(c);
    #     else:
    #         place_cleaned.append(c);

    place_cleaned = place.replace('[','');
    place = place_cleaned.replace(']','');
    return place