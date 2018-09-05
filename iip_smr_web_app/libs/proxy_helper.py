# -*- coding: utf-8 -*-

import logging, os, subprocess
from django.conf import settings
from iip_smr_web_app import settings_app


log = logging.getLogger(__name__)


def rewrite( source, proxy_url, js_rewrite_url ):
    """ Rewrites input html.
        Called by views.proxy() """
    rewritten = source.replace(
        'href="../', 'href="%s' % proxy_url )
    rewritten = rewritten.replace(
        '<script src="doubletreejs/', '<script src="%s' % js_rewrite_url )
    rewritten = rewritten.replace(
        'textRequest.open("GET", "doubletree-data.txt"', 'textRequest.open("GET", "%sdoubletree-data.txt"' % proxy_url )
    rewritten = rewritten.replace(
        'src="../index_search.js"', 'src="http://127.0.0.1:8000/resources/wordcount_labs/index_search.js/"' )
    rewritten = rewritten.replace(
        'src="../levenshtein.min.js"', 'src="http://127.0.0.1:8000/resources/wordcount_labs/levenshtein.min.js/"' )
    rewritten = rewritten.replace(
        '<!DOCTYPE HTML>', '' )
    rewritten = rewritten.replace(
        '<html>', '', 2 )
    log.debug( 'rewritten, ```%s```' % rewritten )
    return rewritten
