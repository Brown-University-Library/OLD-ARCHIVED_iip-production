# -*- coding: utf-8 -*-

import logging, pprint, random, re
import mysolr, requests, solr
from StringIO import StringIO
from django.core.urlresolvers import reverse
from iip_smr_config import settings_app

log = logging.getLogger(__name__)

NUM_ROWS = 40

def facetResults( facet ):
    """ Returns dict of { facet_value_a: count_of_facet_value_a_entries }. """
    try:
        s = solr.SolrConnection( settings_app.SOLR_URL )
        q = s.select( u'*:*', **{u'facet':u'true',u'facet.field':facet,u'rows':u'0',u'facet.limit':u'-1', u'facet.mincount':u'1'} )
        facet_count_dict =q.facet_counts[u'facet_fields'][facet]
        return facet_count_dict
    except Exception as e:
        log.error( u'in common.facetResults(); exception, %s' % unicode(repr(e)) )

def get_log_identifier( request_session=None ):
    """ Returns a log_identifier unicode_string.
        Sets it in the request session if necessary. """
    log_id = unicode( random.randint(1000,9999) )
    if request_session == None:  # cron script writing to log
        pass
    else:
        if u'log_identifier' in request_session:
            log_id = request_session[u'log_identifier']
        else:
            request_session[u'log_identifier'] = log_id
    return log_id


def make_admin_links( session_authz_dict, url_host, log_id ):
    """ Takes authorization session dict;
            makes and returns admin links list of dicts.
        Called by (iip_results) views._get_GET_context() """
    log.debug( u'in common.make_admin_link(); id, `%s`; session_authz_dict, %s' % (log_id, session_authz_dict) )
    if session_authz_dict[u'authorized']:
        admin_links = [
            { u'text': u'[ logout ]',
              u'url': u'%s://%s%s' % (settings_app.URL_SCHEME, url_host, reverse(u'logout_url',)) },
            { u'text': u'edit static pages',
              u'url': u'%s://%s%s' % (settings_app.URL_SCHEME, url_host, reverse(u'edit_info_url')) },
            ]
    else:
        admin_links = [
            { u'text': u'[ admin ]',
              u'url': u'%s://%s%s' % (settings_app.URL_SCHEME, url_host, reverse(u'login_url',)) }
            ]
    return admin_links



def queryCleanup(qstring):
    qstring = qstring.replace('(', '')
    qstring = qstring.replace(')', '')
    qstring = qstring.replace('"', '')
    qstring = qstring.replace('_', ' ')
    qstring = re.sub(r'notBefore\:\[(-?\d*) TO 10000\]', r'dates after \1', qstring)
    qstring = re.sub(r'notAfter\:\[-10000 TO (-?\d*)]', r'dates before \1', qstring)
    qstring = re.sub(r' -(\d+)', r' \1 BCE', qstring)
    qstring = re.sub(r' (\d+)\b(?!\sBCE)', r' \1 CE', qstring)
    return qstring


## paginateRequest

def paginateRequest( qstring, resultsPage, log_id):
    """ Executes solr query on qstring and returns solr.py paginator object, and paginator.page object for given page, and facet-count dict.
        Called by: (views.iip_results()) views._get_POST_context() and views._get_ajax_unistring(). """
    log.debug( u'in common.paginateRequest(); qstring, %s; resultsPage, %s' % (qstring, resultsPage) )
    ( s, q ) = _run_paginator_main_query( qstring, log_id )             # gets solr object and query object
    fq = _run_paginator_facet_query( s, qstring, log_id )               # gets facet-query object
    ( p, pg ) = _run_paginator_page_query( q, resultsPage, log_id )     # gets paginator object and paginator-page object
    f = _run_paginator_facet_counts( fq )                               # gets facet-counts dict
    try:
        dispQstring = queryCleanup(qstring.encode('utf-8'))
        return {'pages': p, 'iipResult': pg, 'qstring':qstring, 'resultsPage': resultsPage, 'facets':f, 'dispQstring': dispQstring}
    except Exception as e:
        log.error( u'in common.paginateRequest(); id, %s; exception, %s' % (log_id, unicode(repr(e))) )
        return False

def _run_paginator_main_query( qstring, log_id ):
    """ Performs a lookup on the query-string; returns solr object and query object.
        Called by paginateRequest()."""
    s = solr.SolrConnection( settings_app.SOLR_URL )
    args = {'rows':NUM_ROWS, 'sort':'inscription_id asc'}
    try:
        q = s.query((qstring.encode('utf-8')),**args)
        log.debug( u'in common._run_paginator_main_query(); id, %s; q created via try' % log_id )
    except Exception as e1:
        q = s.query('*:*', **args)
        log.debug( u'in common._run_paginator_main_query(); id, %s; exception, %s; q created via except' % (log_id, unicode(repr(e1))) )
    return ( s, q )

def _run_paginator_facet_query( s, qstring, log_id ):
    """ Performs a facet-lookup for the query-string; returns facet-query object.
        Called by paginateRequest()."""
    args = {'rows':NUM_ROWS}
    try:
        fq = s.query((qstring.encode('utf-8')),facet='true', facet_field=['region','city','type','physical_type','language','religion'],**args)
    except:
        fq = s.query('*:*',facet='true', facet_field=['region','city','type','physical_type','language','religion'],**args)
    log.debug( u'in common._run_paginator_facet_query(); id, %s; fq is, `%s`; fq.__dict__ is, `%s`' % (log_id, fq, fq.__dict__) )
    return fq

def _run_paginator_page_query( q, resultsPage, log_id ):
    """ Instantiates a paginator object and, from query-results, creates a paginator.page object.
        Called by paginateRequest(). """
    p = solr.SolrPaginator(q, NUM_ROWS)
    try:
        pg = p.page(resultsPage)
    except Exception as e:
        pg = ''
    ## log.debug( u'in common._run_paginator_page_query(); id, %s; pg is, `%s`; pg.__dict__ is, `%s`' % (log_id, pg, pg.__dict__) )
    return ( p, pg )

def _run_paginator_facet_counts( fq ):
    """ Returns facet_count dict from the facet-query object.
        Called by paginateRequest(). """
    try:
        f = fq.facet_counts['facet_fields']
    except:
        f    = ''
    return f

def updateQstring( initial_qstring, session_authz_dict, log_id ):
    """ Adds 'approved' display-status limit to solr query string if user is *not* logged in
          (because if user *is* logged in, display facets are shown explicitly).
        Returns modified_qstring dict.
        Called by: views.iipResults(). """
    if ( (session_authz_dict == None)
         or (not u'authorized' in session_authz_dict)
         or (not session_authz_dict['authorized'] == True) ):
        qstring = u'display_status:(approved) AND ' + initial_qstring if initial_qstring != '' else u'display_status:(approved)'
    else:
        qstring = initial_qstring
    return { 'modified_qstring': qstring }

## eof
