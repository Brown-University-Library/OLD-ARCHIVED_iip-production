# -*- coding: utf-8 -*-

import json, logging, pprint, re
# import solr, requests
import requests
import xml.etree.ElementTree as ET
from django import forms
from iip_smr_web_app import common, settings_app


log = logging.getLogger(__name__)

def doDateEra(self,f,v):
    if f == u'notAfter' and v:
        if self.cleaned_data['beforeDateEra'] == 'bce':
            v = u"-%s" % v.replace('-','')
        elif self.cleaned_data['beforeDateEra'] == 'ce':
            v = u"%s" % v.replace('-','')
        return u"[-10000 TO %s]" % v
    if f == u'notBefore' and v:
        if self.cleaned_data['afterDateEra'] == 'bce':
            v = u"-%s" % v.replace('-','')
        elif self.cleaned_data['afterDateEra'] == 'ce':
            v = u"%s" % v.replace('-','')
        return u"[%s TO 10000]" % v

def make_vocab_list(vocab_dict, solr_facet):
    outlist = []
    for item in solr_facet:
        if item:
            if item in vocab_dict.keys():
                outlist.append((item, vocab_dict[item]))
            else:
                outlist.append((item, item))
    return sorted(outlist, key=lambda x: x[1].lower())



class SearchForm( forms.Form ):

    log.debug( 'SearchForm() class loaded' )

    def __init__(self, *args, **kwargs):
        """ Builds choices dynamically.
            <https://stackoverflow.com/questions/3419997/creating-a-dynamic-choice-field> """
        #
        super(SearchForm, self).__init__(*args, **kwargs)
        log.debug( 'SearchForm() instantiated' )
        log.debug( '*args, ```%s```' % args )
        log.debug( '**kwargs, ```%s```' % kwargs )
        #
        # url = 'https://127.0.0.1/test/dev/django_choices.json'
        # r = requests.get( url )
        # log.debug( 'r.content, ```%s```' % r.content )
        # self.choice_places = json.loads( r.content )
        #
        self.choice_places = [(item, item) for item in sorted( common.facetResults('placeMenu').keys()) if item]
        # self.fields['place'] = forms.MultipleChoiceField(required=False, choices=self.choice_places, widget=forms.SelectMultiple(attrs={'size':'10'}))
        self.fields['place'] = forms.MultipleChoiceField(required=False, choices=self.choice_places, widget=forms.CheckboxSelectMultiple())
        #
        self.vocab_request = requests.get("https://cds.library.brown.edu/projects/iip/include_taxonomies.xml")
        self.vocab = ET.fromstring(self.vocab_request.content)
        self.taxonomies = self.vocab.findall('{http://www.tei-c.org/ns/1.0}taxonomy')
        #
        log.debug( 'type(self.taxonomies), `%s`' % type(self.taxonomies) )
        log.debug( 'self.taxonomies[0].attrib.values(), ```%s```' % self.taxonomies[0].attrib.values() )
        log.debug( 'tax.attrib.values(), ```%s```' % [tax.attrib.values() for tax in self.taxonomies] )
        # self.type_tax = [tax for tax in self.taxonomies if tax.attrib.values()[0] == 'IIP-genre'][0]
        self.type_tax = [tax for tax in self.taxonomies if list( tax.attrib.values() )[0] == 'IIP-genre'][0]
        # self.types_dict = dict([(element.attrib.values()[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text) for element in self.type_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        #self.types_dict = dict([( list(element.attrib.values())[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text ) for element in self.type_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.types_dict = dict([(list(element.attrib.values())[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text.lstrip('-')) for element in self.type_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.choice_types = make_vocab_list( self.types_dict, sorted( common.facetResults('type').keys()) )
        # self.fields['type'] = forms.MultipleChoiceField(required=False, choices=self.choice_types, widget=forms.SelectMultiple(attrs={'size':'7'}))
        self.fields['type'] = forms.MultipleChoiceField(required=False, choices=self.choice_types, widget=forms.CheckboxSelectMultiple())
        #
        # self.phys_types_tax = [tax for tax in self.taxonomies if tax.attrib.values()[0] == 'IIP-form'][0]
        self.phys_types_tax = [tax for tax in self.taxonomies if list( tax.attrib.values() )[0] == 'IIP-form'][0]
        # self.physical_types_dict = dict([(element.attrib.values()[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text) for element in self.phys_types_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.physical_types_dict = dict([( list(element.attrib.values())[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text ) for element in self.phys_types_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.physical_types = make_vocab_list(self.physical_types_dict, sorted( common.facetResults('physical_type').keys()))
        # self.fields['physical_type'] = forms.MultipleChoiceField(required=False, choices=self.physical_types, widget=forms.SelectMultiple(attrs={'size':'7'}))
        self.fields['physical_type'] = forms.MultipleChoiceField(required=False, choices=self.physical_types, widget=forms.CheckboxSelectMultiple())
        #
        # self.religions_tax = [tax for tax in self.taxonomies if tax.attrib.values()[0] == 'IIP-religion'][0]
        self.religions_tax = [tax for tax in self.taxonomies if list( tax.attrib.values() )[0] == 'IIP-religion'][0]
        # self.religions = [(element.attrib.values()[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text) for element in self.religions_tax.findall('{http://www.tei-c.org/ns/1.0}category')]
        self.religions = [( list(element.attrib.values())[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text ) for element in self.religions_tax.findall('{http://www.tei-c.org/ns/1.0}category')]
        # self.fields['religion'] = forms.MultipleChoiceField(required=False, choices=self.religions, widget=forms.CheckboxSelectMultiple)
        self.fields['religion'] = forms.MultipleChoiceField(required=False, choices=self.religions, widget=forms.CheckboxSelectMultiple(attrs={'class': 'styled'}))
        #
        self.languages_dict = {
            "he":"Hebrew",
            "la": "Latin",
            "grc": "Greek",
            "arc": "Aramaic",
            "x-unknown":"Unknown"
            }
        self.languages = make_vocab_list(self.languages_dict, sorted( common.facetResults('language').keys()))
        # self.fields['language'] = forms.MultipleChoiceField(required=False, choices=self.languages, widget=forms.CheckboxSelectMultiple)
        self.fields['language'] = forms.MultipleChoiceField(required=False, choices=self.languages, widget=forms.CheckboxSelectMultiple())

        # self.material_tax = [tax for tax in self.taxonomies if tax.attrib.values()[0] == 'IIP-materials'][0]
        self.material_tax = [tax for tax in self.taxonomies if list(tax.attrib.values())[0] == 'IIP-materials'][0]
        # self.materials_dict = dict([(element.attrib.values()[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text) for element in self.material_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.materials_dict = dict([(list(element.attrib.values())[0], element.find('{http://www.tei-c.org/ns/1.0}catDesc').text) for element in self.material_tax.findall('{http://www.tei-c.org/ns/1.0}category')])
        self.materials = make_vocab_list( self.materials_dict, sorted( common.facetResults('material').keys()) )
        self.fields['material'] = forms.MultipleChoiceField(required=False, choices=self.materials, widget=forms.CheckboxSelectMultiple())
    text = forms.CharField(required=False)
    metadata = forms.CharField(required=False)
    figure = forms.CharField(required=False)
    #
    DISPLAY_STATUSES = [
    ('approved', 'Approved'),  # ( 'value', 'label' )
    ('to_approve', 'To Approve'),
    ('to_correct', 'To Correct') ]
    display_status = forms.MultipleChoiceField(required=False, choices=DISPLAY_STATUSES, widget=forms.CheckboxSelectMultiple)
    #
    notBefore = forms.CharField(required=False, max_length=5)
    notAfter = forms.CharField(required=False, max_length=5)
    afterDateEra = forms.ChoiceField(required=False, choices=(('bce','BCE'),('ce','CE')), widget=forms.RadioSelect)
    beforeDateEra = forms.ChoiceField(required=False, choices=(('bce','BCE'),('ce','CE')), widget=forms.RadioSelect)
    # select_multiple = dict.fromkeys(['type', 'physical_type', 'language', 'religion', 'material'], "on")
    type_ = forms.ChoiceField(required=True, choices=(('or', 'OR'), ('and', 'AND')), widget = forms.RadioSelect(attrs={'class': 'select-multiple-toggle'}), label="select")
    physical_type_ = forms.ChoiceField(required=True, choices=(('or', 'OR'), ('and', 'AND')), widget = forms.RadioSelect(attrs={'class': 'select-multiple-toggle'}))
    language_ = forms.ChoiceField(required=True, choices=(('or', 'OR'), ('and', 'AND')), widget = forms.RadioSelect(attrs={'class': 'select-multiple-toggle'}))
    religion_ = forms.ChoiceField(required=True, choices=(('or', 'OR'), ('and', 'AND')), widget = forms.RadioSelect(attrs={'class': 'select-multiple-toggle'}))
    material_ = forms.ChoiceField(required=True, choices=(('or', 'OR'), ('and', 'AND')), widget = forms.RadioSelect(attrs={'class': 'select-multiple-toggle'}))

    # url = 'https://127.0.0.1/test/dev/django_choices.json'
    # r = requests.get( url )
    # log.debug( 'r.content, ```%s```' % r.content )
    # places = json.loads( r.content )
    # place = forms.MultipleChoiceField(required=False, choices=places, widget=forms.SelectMultiple(attrs={'size':'10'}))

    def generateSolrQuery(self):
        search_fields = ('text','metadata','figure','region','city','place','type','physical_type','language','religion','notBefore','notAfter', 'display_status')
        response = ''
        first = True
        concat_operators = {
            'type': self.cleaned_data['type_'].upper(),
            'physical_type': self.cleaned_data['physical_type_'].upper(),
            'language': self.cleaned_data['language_'].upper(),
            'religion': self.cleaned_data['religion_'].upper(),
            'material': self.cleaned_data['material_'].upper()
        }
        log.debug( 'concat_operators, ```%s```' % concat_operators )
        # print(self.cleaned_data.items())
        log.debug( 'self.cleaned_data.items(), ```%s```' % self.cleaned_data.items() )
        for f,v in self.cleaned_data.items(): # f = facet (place, type, etc.), v = value (["altar, amphora"])
            #The following is specific to the date-encoding in the IIP & US Epigraphy projects
            #If youre using this code for other projects, you probably want to omit them
            if ((f == u'notBefore') or (f == u'notAfter')) and v:
                v = doDateEra(self,f,v)
            # End custom blocks
            elif v:
                if isinstance(v, list): #if multiple values selected for a facet (e.g. v = ["altar, amphora"])
                    vListFirst = True
                    vlist = ''
                    for c in v:
                        if re.search( '\s', str(c) ):
                            c = u"\"%s\"" % c
                        if vListFirst:
                            vListFirst = False
                        else:
                            vlist += (' ' + concat_operators[f] + ' ' + f + ":")
                        vlist += u"%s" % c
                    v = u"%s" % vlist
                else:
                    if re.search('\s', str(v)):
                        v = u"\"%s\"" % v
            if f and v:
                if f in search_fields:
                    print(f)
                    print(v)
                    if first:
                        first = False
                    else:
                        if(v != ''): response += " AND "
                    if(v != ''): response += u"(%s:%s)" % (f,v)
        print('response')
        print(response)
        return response
