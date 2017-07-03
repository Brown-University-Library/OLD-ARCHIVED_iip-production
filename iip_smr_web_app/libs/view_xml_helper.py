# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
import requests


log = logging.getLogger(__name__)


class XmlPrepper( object ):
    """ Contains functions for accessing github xml file and propogating cache info.
        Helper for views.view_xml() """

    def prep_lookup_headers( self, meta_dct ):
        """ Prepares headers for the requests module hit to the github xml file.
            Called by views.view_xml() """
        hdrs = {}
        if 'HTTP_IF_NONE_MATCH' in meta_dct:
            hdrs['If-None-Match'] = meta_dct['HTTP_IF_NONE_MATCH']
        if 'HTTP_IF_MODIFIED_SINCE' in meta_dct:
            hdrs['If-Modified-Since'] = meta_dct['HTTP_IF_MODIFIED_SINCE']
        log.debug( 'hdrs, `%s`' % hdrs )
        return hdrs

    def enhance_response( self, response, lookup_response ):
        """ Populates initialized response-object with data from the xml lookup_response.
            Called by views.view_xml() """
        response.status_code = lookup_response.status_code
        if lookup_response.status_code == requests.codes.ok:
            response.content = lookup_response.content
            response["Content-Type"] = "text/xml"
        for hdr in ['ETag', 'Expires', 'Last-Modified', 'Cache-Control', 'Age', 'Source-Age' ]:  # propogates cache info
            if hdr in lookup_response.headers:
                response[hdr] = lookup_response.headers[hdr]
        return response
