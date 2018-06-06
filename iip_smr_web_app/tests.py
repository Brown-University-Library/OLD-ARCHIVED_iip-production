# -*- coding: utf-8 -*-

import json, logging, pprint
# import requests, solr
import requests
from iip_smr_web_app import common, models, settings_app
from django.test import Client, TestCase
# from models import Processor, ProcessorUtils
# from models import ProcessorUtils


log = logging.getLogger(__name__)


class ResourcesPageTest(TestCase):
    """ Tests responses for resource pages. """
    fixtures = ['static_pages.json']

    # def setUp(self):
    #     self.client = Client()

    def test_static_urls(self):
        """ Checks '/about' and '/resources urls'. """
        response = self.client.get( '/about/why_inscription/' )  # project root part of url is assumed
        log.debug( 'response, `%s`' % response )
        self.assertEqual( 200, response.status_code )
        response = self.client.get( '/resources/transcription-symbols/' )
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
