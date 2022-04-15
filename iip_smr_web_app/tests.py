# -*- coding: utf-8 -*-

import json
import logging
import pprint
from collections import OrderedDict

import requests
from django.test import Client, TestCase
from iip_smr_web_app import common, models, settings_app
from iip_smr_web_app.libs.wordlist import wordlist


log = logging.getLogger(__name__)


class GreekWordsTest (TestCase):
    """ Checks sorting of greek words. """

    def test_sort_greek_words(self):
        """ Checks greek word sort.
            Note: tested function is not actually used.
            Possible TODO: refactor wordlist.make_key_lemma_dct() to use the sort_greek_words() function.
            For now, this test and the function serve to illustrate a method for performing the sort -- which is used in make_key_lemma_dct(). """
        unsorted_words = [
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
        sorted_words = wordlist.sort_greek_words( unsorted_words )
        self.assertEqual( [
            'α',
            'ἀβάβη',
            'ἃμα',
            'ἒνθα',
            'ἐπί',
            'έρισα',
            'ἡαρίβος',
            'ἠλίας',
            'ἥμος',
            'ί',
            'ἲησοῦς',
            'ἵνδω',
            'ὧδε',
            'ὠσείς',
            'ὥσπερ'
            ],
            sorted_words
        )

    def test_make_key_lemma_dct(self):
        """ Given list of greek words,
            returns an OrderedDict where the keys are a sorted unique list of letters without diacritics,
            and the value for each key is the word the key-character will link to.
            An example (using English with no diacritics to illustrate the linkage point)...
            - given the wordlist [ 'rose', 'bore', 'red', 'bid' ]
            - the returned data would be OrderedDict([ ('b', 'bid'), ('r', 'red') ])
              ...because in a list of sorted words, 'bid' is the first 'b' word, etc. 
            This is used in the greek wordlist page to link the list of alphabetical characters to the first appropriate word in the list.  """
        unsorted_words = [
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
        sorted_ordered_dct = wordlist.make_key_lemma_dct( unsorted_words )
        self.assertEqual( 
            OrderedDict([
                ('α', 'α'), 
                ('ε', 'ἒνθα'), 
                ('η', 'ἡαρίβος'), 
                ('ι', 'ί'), 
                ('ω', 'ὧδε')
            ]),
            sorted_ordered_dct
         )
    
    ## end class GreekWordsTest()


class UrlTest( TestCase ):
    """ Checks urls. """

    def test_root_url_no_slash(self):
        """ Checks '/root_url redirect (no appended slash)'. """
        response = self.client.get( '' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url: str = response['location']
        self.assertEqual(  '/index/', redirect_url )

    def test_root_url_slash(self):
        """ Checks '/root_url/ redirect (with appended slash)'. """
        response = self.client.get( '/' )  # project root part of url is assumed
        self.assertEqual( 302, response.status_code )  # permanent redirect
        redirect_url: str = response['location']
        self.assertEqual(  '/index/', redirect_url )

    def test_mapsearch_form(self):
        """ Checks 'mapsearch' form. """
        response = self.client.get( '/mapsearch/' )
        self.assertEqual( 200, response.status_code )
        self.assertTrue(  b'the search box' in response.content )

    def test_mapsearch_results(self):
        """ Checks 'mapsearch' results. """
        response = self.client.get( '/mapsearch/?q=(material:lead)' )
        self.assertEqual( 200, response.status_code )
        self.assertTrue(  b'caes0501' in response.content.lower() )
        self.assertTrue(  b'caesarea, 6th-7th century' in response.content.lower() )

    def test_mapsearch_results_data(self):
        """ Checks 'mapsearch' results json. """
        response = self.client.get( '/mapsearch/?q=(material:lead)&format=json' )
        self.assertEqual( 200, response.status_code )
        is_json = False
        try:
            json.loads( response.content )
            is_json = True
        except:
            log.exception( 'not json!' )
        self.assertEqual( is_json, True )

    # ------------------------------
    # testing resources menu - start
    # ------------------------------

    def test_about__resources_menu(self):
        """ Checks `about` landing page resources menu. """
        response = self.client.get( '/about/' )
        expecteds = [ b'Bibliography', b'Conventional Transcription Symbols', b'Glossary', b'Guide to Searching', b'Timeline', b'Wordlist Beta' ]
        html = response.content
        self.assertEqual( bytes, type(html) )
        for expected in expecteds:
            try:
                self.assertTrue( expected in html )
            except:
                raise Exception( f'not found, ``{expected}``' )

    def test_about_selection__resources_menu(self):
        """ Checks `about` landing page resources menu -- when one of the about sub-options is in the url. """
        log.debug( 'starting test' )
        ## add data to test-db
        why_inscription_static_page = models.StaticPage( slug='why_inscription', title='Why Inscription' )
        why_inscription_static_page.save()
        bib_static_page = models.StaticPage( slug='bibliography', title='Bibliography' )
        bib_static_page.save()
        ## now the test
        response = self.client.get( '/about/why_inscription/' )
        expecteds = [ b'Bibliography', b'Conventional Transcription Symbols', b'Glossary', b'Guide to Searching', b'Timeline', b'Wordlist Beta' ]
        html = response.content
        log.debug( f'html, ``{html}``' )
        self.assertEqual( bytes, type(html) )
        for expected in expecteds:
            try:
                self.assertTrue( expected in html )
            except:
                raise Exception( f'not found, ``{expected}``' )

    def test_search__resources_menu(self):
        """ Checks `search` landing page resources menu. """
        response = self.client.get( '/mapsearch/' )
        expecteds = [ b'Bibliography', b'Conventional Transcription Symbols', b'Glossary', b'Guide to Searching', b'Timeline', b'Wordlist Beta' ]
        html = response.content
        self.assertEqual( bytes, type(html) )
        for expected in expecteds:
            try:
                self.assertTrue( expected in html )
            except:
                raise Exception( f'not found, ``{expected}``' )

    def test_stories__resources_menu(self):
        """ Checks `stories` landing page resources menu. """
        response = self.client.get( '/stories/' )
        expecteds = [ b'Bibliography', b'Conventional Transcription Symbols', b'Glossary', b'Guide to Searching', b'Timeline', b'Wordlist Beta' ]
        html = response.content
        self.assertEqual( bytes, type(html) )
        for expected in expecteds:
            try:
                self.assertTrue( expected in html )
            except:
                raise Exception( f'not found, ``{expected}``' )

    def test_resources_selection__resources_menu(self):
        """ Checks `resources` page resources menu -- when one of the resources sub-options is in the url. """
        ## add entry to test-db
        bib_static_page = models.StaticPage( slug='bibliography', title='Bibliography' )
        bib_static_page.save()
        ## now the test
        response = self.client.get( '/resources/bibliography/' )
        expecteds = [ b'Bibliography', b'Conventional Transcription Symbols', b'Glossary', b'Guide to Searching', b'Timeline', b'Wordlist Beta' ]
        html = response.content
        self.assertEqual( bytes, type(html) )
        log.debug( f'html, ``{html}``' )
        for expected in expecteds:
            try:
                self.assertTrue( expected in html )
            except:
                raise Exception( f'not found, ``{expected}``' )

    # ----------------------------
    # testing resources menu - end
    # ----------------------------

    ## end class UrlTest


class ResourcesPageTest(TestCase):
    """ Tests responses for resource pages. """
    fixtures = ['static_pages.json']

    def test_static_urls(self):
        """ Checks '/about' and '/resources urls'. """
        response = self.client.get( '/about/why_inscription/' )  # project root part of url is assumed
        log.debug( 'response, `%s`' % response )
        self.assertEqual( 200, response.status_code )
        response = self.client.get( '/resources/conventional_transcription_symbols/' )
        log.debug( 'response, `%s`' % response )
        self.assertEqual( 200, response.status_code )

    ## end class ResourcesPageTest()


class CommonTest( TestCase ):
    """ Tests functions in 'common.py'. """

    # def test_facetResults( self ):
    #     """ Checks type of data returned from query. """
    #     facet_count_dict = common.facetResults( facet=u'placeMenu' )
    #     log.debug( u'facet_count_dict, ```%s```' % pprint.pformat(facet_count_dict) )
    #     for place in [  u'Galilee', u'Jordan', u'Judaea' ]:
    #         self.assertEqual(
    #             True,
    #             place in facet_count_dict.keys()
    #             )
    #         self.assertEqual(
    #             True,
    #             type(facet_count_dict[place]) == int
    #             )

    # def test_paginateRequest( self ):
    #     """ Checks data returned by paginateRequest. """
    #     sent_qstring = u'display_status:(approved) AND language:(Aramaic)'
    #     sent_results_page = 3
    #     data = common.paginateRequest( qstring=sent_qstring, resultsPage=sent_results_page, log_id=u'123' )
    #     self.assertEqual(
    #         [u'dispQstring', u'facets', u'iipResult', u'pages', u'qstring', u'resultsPage'],
    #         sorted( data.keys() )
    #         )
    #     self.assertEqual(
    #         u'display status:approved AND language:Aramaic',
    #         data[u'dispQstring']
    #         )
    #     self.assertEqual(
    #         [u'city', u'language', u'physical_type', u'region', u'religion', u'type'],
    #         sorted( data[u'facets'].keys() )
    #         )
    #     self.assertEqual(
    #         sent_qstring,
    #         data[u'qstring']
    #         )
    #     self.assertEqual(
    #         True,
    #         u'<solr.paginator.SolrPaginator instance' in unicode(repr(data[u'pages']))
    #         )
    #     self.assertEqual(
    #         sent_results_page,
    #         data[u'resultsPage']
    #         )

    def test_update_q_string( self ):
        """ Tests modification of solr query string. """
        # log.warning( 'starting test' )
        initial_qstring = u'foo'
        log_identifier = u'bar'
        # no session_authz_dict
        session_authz_dict = None
        self.assertEqual(
            {'modified_qstring': u'display_status:(approved) AND foo'},
            common.updateQstring(initial_qstring, session_authz_dict, log_identifier) )
        # session_authz_dict, but no 'authorized' key
        session_authz_dict = { u'some_key': u'some_value' }
        self.assertEqual(
            {'modified_qstring': u'display_status:(approved) AND foo'},
            common.updateQstring(initial_qstring, session_authz_dict, log_identifier) )
        # session_authz_dict, and 'authorized' key, but authorized not True
        session_authz_dict = { u'authorized': u'other_than_true' }
        self.assertEqual(
            {'modified_qstring': u'display_status:(approved) AND foo'},
            common.updateQstring(initial_qstring, session_authz_dict, log_identifier) )
        # life good
        session_authz_dict = { u'authorized': True }
        self.assertEqual(
            {'modified_qstring': u'foo'},
            common.updateQstring(initial_qstring, session_authz_dict, log_identifier) )

#     def test_validate_xml( self ):
#         """ Tests validation. """
#         schema = u"""<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">
# <xsd:element name="a" type="AType"/>
#     <xsd:complexType name="AType">
#         <xsd:sequence>
#             <xsd:element name="b" type="xsd:string" />
#         </xsd:sequence>
#     </xsd:complexType>
# </xsd:schema>"""
#         ## valid
#         xml = u"""<?xml version="1.0" encoding="utf-8"?><a><b></b></a>"""
#         data_dict = common.validate_xml( xml=xml, schema=schema )
#         self.assertEqual(
#             True,
#             data_dict[u'validate_result'] )
#         ## not valid
#         xml = u"""<?xml version="1.0" encoding="utf-8"?><a><c></c></a>"""
#         data_dict = common.validate_xml( xml=xml, schema=schema )
#         self.assertEqual(
#             False,
#             data_dict[u'validate_result'] )

    # def test_check_xml_wellformedness(self):
    #     """ Tests that xml is well-formed.
    #         TODO: eliminate this test and the code once there's a schema, and instead use validate_xml() """
    #     ## good
    #     xml = u"""<?xml version="1.0" encoding="utf-8"?><a><b></b></a>"""
    #     data_dict = common.check_xml_wellformedness( xml )
    #     self.assertEqual(
    #         True,
    #         data_dict[u'well_formed'] )
    #     ## bad
    #     xml = u"""<a><b><b></a>"""
    #     data_dict = common.check_xml_wellformedness( xml )
    #     self.assertEqual(
    #         False,
    #         data_dict[u'well_formed'] )

# eof
