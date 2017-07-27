# -*- coding: utf-8 -*-

import datetime, json, logging, os, pprint, re
import solr, requests
from .models import StaticPage
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from iip_smr_web_app import common, models, settings_app
from iip_smr_web_app import forms
from iip_smr_web_app.libs.view_xml_helper import XmlPrepper
from iip_smr_web_app.libs import ajax_snippet


log = logging.getLogger(__name__)


def temp( request ):
    message = 'Yay!!! %s' % str( datetime.datetime.now() )
    log.debug( 'test log debug entry' )
    log.info( 'test log info entry' )
    log.error( 'test log error entry' )
    return HttpResponse( message )


## search and results ##

def results( request ):
    """ Handles /results/ GET, POST, and ajax-GET. """
    def _get_results_context( request, log_id ):
        """ Returns correct context for POST.
            Called by results() """
        log.debug( 'starting' )
        context = {}
        request.encoding = u'utf-8'

        form = forms.SearchForm( request.POST )  # form bound to the POST data

        resultsPage = 1
        qstring_provided = None
        if request.method == u'GET':
            qstring_provided = request.GET.get("q", None)
            resultsPage = int(request.GET.get('resultsPage', resultsPage))

        if form.is_valid() or qstring_provided:
            initial_qstring = ""
            if qstring_provided:
                initial_qstring = qstring_provided
            else:
                initial_qstring = form.generateSolrQuery()

            updated_qstring = common.updateQstring(
                initial_qstring=initial_qstring, session_authz_dict=request.session['authz_info'], log_id=common.get_log_identifier(request.session) )['modified_qstring']
            context = common.paginateRequest( qstring=updated_qstring, resultsPage=resultsPage, log_id=common.get_log_identifier(request.session) )
            log.debug( 'context, ```%s```' % pprint.pformat(context) )
            context[u'session_authz_info'] = request.session[u'authz_info']
            context[u'admin_links'] = common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id )
            context[u'initial_qstring'] = initial_qstring
        log.debug( 'context.keys(), ```%s```' % pprint.pformat(sorted(context.keys())) )
        log.debug( 'type(context), `%s`' % type(context) )



        # results = context['iipResult']
        # log.debug( 'type(results), `%s`' % type(results) )
        # for (i, result) in enumerate(results.object_list):
        #     log.debug( 'type(result), `%s`' % type(result) )
        #     log.debug( 'result, `%s`' % result )
        #     if i > 0:
        #         break
        #     1/0


        return context

    def _get_ajax_unistring( request ):
        """ Returns unicode string based on ajax update.
            Called by results() """
        log_id = common.get_log_identifier(request.session)
        log.info( 'id, `%s`; starting' % log_id )
        initial_qstring = request.GET.get( u'qstring', u'*:*' )
        updated_qstring = common.updateQstring( initial_qstring, request.session[u'authz_info'], log_id )[u'modified_qstring']
        resultsPage = int( request.GET[u'resultsPage'] )
        context = common.paginateRequest(
            qstring=updated_qstring, resultsPage=resultsPage, log_id=log_id )
        return_str = ajax_snippet.render_block_to_string(u'iip_search_templates/results.html', u'content', context)
        return unicode( return_str )

    def _get_searchform_context( request, log_id ):
        """ Returns correct context for GET.
            Called by results() """
        log.debug( '_get_searchform_context() starting' )
        if not u'authz_info' in request.session:
            request.session[u'authz_info'] = { u'authorized': False }
        # form = SearchForm()  # an unbound form
        form = forms.SearchForm()  # an unbound form
        log.debug( 'form, `%s`' % repr(form) )
        # place_field_object = form.fields['place']
        # place_field_object.choices = [(item, item) for item in sorted( common.facetResults('placeMenu').keys()) if item]
        # form.fields['place'] = place_field_object
        context = {
            u'form': form,
            u'session_authz_info': request.session[u'authz_info'],
            u'settings_app': settings_app,
            u'admin_links': common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id )
            }
        log.debug( 'context, ```%s```' % pprint.pformat(context) )
        return context
    log_id = common.get_log_identifier( request.session )
    log.info( 'id, `%s`; starting' % log_id )
    if not u'authz_info' in request.session:
        request.session[u'authz_info'] = { u'authorized': False }
    if request.method == u'POST': # form has been submitted by user
        log.debug( 'POST, search-form was submitted by user' )
        request.encoding = u'utf-8'
        form = forms.SearchForm(request.POST)
        if not form.is_valid():
            log.debug( 'form not valid, redirecting')
            redirect_url = '%s://%s%s?q=*:*' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'results_url') )
            log.debug( 'redirect_url for non-valid form, ```%s```' % redirect_url )
            return HttpResponseRedirect( redirect_url )
        qstring = form.generateSolrQuery()
        # e.g. http://library.brown.edu/cds/projects/iip/results?q=*:*
        redirect_url = '%s://%s%s?q=%s' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'results_url'), qstring )
        log.debug( 'redirect_url for valid form, ```%s```' % redirect_url )
        return HttpResponseRedirect( redirect_url )
    if request.method == u'GET' and request.GET.get(u'q', None) != None:
        log.debug( 'GET, with params, hit solr and show results' )
        return render( request, u'iip_search_templates/results.html', _get_results_context(request, log_id) )
    elif request.is_ajax():  # user has requested another page, a facet, etc.
        log.debug( 'request.is_axax() is True' )
        return HttpResponse( _get_ajax_unistring(request) )
    else:  # regular GET, no params
        log.debug( 'GET, no params, show search form' )
        return render( request, u'iip_search_templates/search_form.html', _get_searchform_context(request, log_id) )



## view inscription ##

biblRegex = re.compile(r'bibl=(.*)\.xml\|nType=(.*)\|n=(.*)')

def viewinscr(request, inscrid):
    """ Handles view-inscription GET with new Javascript and Zotero bibliography. """

    def _bib_tuple_or_none(s):
        t = biblRegex.match(s)
        if t:
            return t.groups()
        elif s == "ms":
            return ("ms", None, None)
        else:
            return None

    # Prepare an inscription
    def _prepare_viewinscr_get_data (request, inscrid):
        """ Prepares data for regular or ajax GET.
                Returns a tuple of vars.
            Called by viewinscr(). """
        log.debug( u'in _prepare_viewinscr_get_data(); starting' )
        log_id = common.get_log_identifier( request.session )
        q = _call_viewinsc_solr( inscrid )  # The results of the solr query to find the inscription. q.results is list of dictionaries of values.
        current_display_status = _update_viewinscr_display_status( request, q )
        z_bibids_initial = [_bib_tuple_or_none(x) for x in q.results[0]['bibl']]
        z_bibids = {}
        for entry in z_bibids_initial:
            if not entry:
                continue
            bibid, ntype, n = entry
            if(not bibid in z_bibids):
                z_bibids[bibid] = []
            if(not (ntype, n) in z_bibids[bibid]):
                z_bibids[bibid].append((ntype, n))
        specific_sources = dict()
        specific_sources['transcription'] = _bib_tuple_or_none(q.results[0]['biblTranscription'][0]) if 'biblTranscription' in q.results[0] else ""
        specific_sources['translation'] = _bib_tuple_or_none(q.results[0]['biblTranslation'][0]) if 'biblTranslation' in q.results[0] else ""
        specific_sources['diplomatic'] = _bib_tuple_or_none(q.results[0]['biblDiplomatic'][0]) if 'biblDiplomatic' in q.results[0] else ""

        view_xml_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'xml_url', kwargs={u'inscription_id':inscrid})  )
        current_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'inscription_url', kwargs={u'inscrid':inscrid})  )
        return ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url )

    def _setup_viewinscr( request ):
        """ Takes request;
                updates session with authz_info and log_id;
                returns log_id.
            Called by viewinscr() """
        log.debug( u'in _setup_viewinscr(); starting' )
        if not u'authz_info' in request.session:
            request.session[u'authz_info'] = { u'authorized': False }
        log_id = common.get_log_identifier( request.session )
        return log_id

    def _call_viewinsc_solr( inscription_id ):
        """ Hits solr with inscription-id.
                Returns a solrpy query-object.
            Called by _prepare_viewinscr_get_data(). """
        s = solr.SolrConnection( settings_app.SOLR_URL )
        qstring = u'inscription_id:%s' % inscription_id
        try:
            q = s.query(qstring)
        except:
            q = s.query('*:*', **args)
        return q

    def _update_viewinscr_display_status( request, q ):
        """ Takes request and solrypy query object.
                Updates session  display-status.
                Returns current display-status.
            Called by _prepare_viewinscr_get_data(). """
        current_display_status = u'init'
        if int( q.numFound ) > 0:
            current_display_status = q.results[0]['display_status']
            request.session['current_display_status'] = current_display_status
        return current_display_status

    def _prepare_viewinscr_ajax_get_response( q, z_bibids, specific_sources, view_xml_url ):
        """ Returns view-inscription response-object for ajax GET.
            Called by viewinscr() """
        log.debug( u'in _prepare_viewinscr_ajax_get_response(); starting' )
        context = {
            'inscription': q,
            'z_ids': z_bibids,
            'biblDiplomatic' : specific_sources['diplomatic'],
            'biblTranscription' : specific_sources['transcription'],
            'biblTranslation' : specific_sources['translation'],
            'biblioFull': False,
            'view_xml_url': view_xml_url }
        return_str = ajax_snippet.render_block_to_string( 'iip_search_templates/viewinscr.html', 'viewinscr', context )
        return_response = HttpResponse( return_str )
        return return_response

    def _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id ):
        """ Returns view-inscription response-object for regular GET.
            Called by viewinscr() """
        log.debug( u'in _prepare_viewinscr_plain_get_response(); starting' )
        context = {
            'inscription': q,
            'z_ids': z_bibids,
            'biblDiplomatic' : specific_sources['diplomatic'],
            'biblTranscription' : specific_sources['transcription'],
            'biblTranslation' : specific_sources['translation'],
            'biblioFull': True,
            'chosen_display_status': current_display_status,
            'inscription_id': inscrid,
            'session_authz_info': request.session['authz_info'],
            'admin_links': common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id ),
            'view_xml_url': view_xml_url,
            'current_url': current_url,
            }
        # log.debug( u'in _prepare_viewinscr_plain_get_response(); context, %s' % pprint.pformat(context) )
        return_response = render( request, u'iip_search_templates/viewinscr.html', context )
        return return_response

    log_id = _setup_viewinscr( request )
    log.info( u'in viewinscr(); id, %s; starting' % log_id )
    ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url ) = _prepare_viewinscr_get_data( request, inscrid )
    if request.is_ajax():
        return_response = _prepare_viewinscr_ajax_get_response( q, z_bibids, specific_sources, view_xml_url )
    else:
        return_response = _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id )
    return return_response


## api ##

def api_wrapper( request ):
    old_params = dict(request.GET)
    params = dict([(x.replace('.', '_'), old_params[x] if len(old_params[x]) > 1 else old_params[x][0]) for x in old_params])
    params['wt'] = 'json'
    if('q' in params and params['q']): params['q'] += " AND display_status:approved"
    s = solr.SolrConnection( settings_app.SOLR_URL )

    r = s.raw_query(**params)

    resp = HttpResponse( str(r), content_type="application/json" )
    resp['Access-Control-Allow-Origin'] = "*"

    return resp

## login ##

def login( request ):
    """ Takes shib-eppn or 'dev_auth_hack' parameter (if enabled for non-shibbolized development) and checks it agains settings list of LEGIT_ADMINS. """
    def _check_shib( request, log_id ):
        """ Takes request;
                examines it for shib info and updates request.session if necessary;
                returns True or False.
            Called by login() """
        log.info( u'in views._check_shib(); id, %s; starting' % log_id )
        return_val = False
        if 'Shibboleth-eppn' in request.META:
            if request.META['Shibboleth-eppn'] in settings_app.LEGIT_ADMINS:  # authorization passed
              request.session['authz_info'] = { 'authorized': True, 'firstname': request.META['Shibboleth-givenName'] }
              return_val = True
        return return_val

    def _check_dev_auth_hack( request, log_id ):
        """ Takes request;
                examines it, and settings, for dev_auth_hack and updates request.session if necessary.
            Called by login() """
        log.info( u'in views._check_dev_auth_hack(); id, %s; starting' % log_id )
        if 'dev_auth_hack' in request.GET and settings_app.DEV_AUTH_HACK == 'enabled':
            log.info( u'in views._check_dev_auth_hack(); id, %s; dev_auth_hack exists and is enabled' % log_id )
            if request.GET['dev_auth_hack'] in settings_app.LEGIT_ADMINS:
                log.info( u'in views._check_dev_auth_hack(); id, %s; param is a legit-admin' % log_id )
                request.session['authz_info'] = { 'authorized': True, 'firstname': request.GET['dev_auth_hack'] }
                log.info( u'in views._check_dev_auth_hack(); id, %s; session authorization to True' % log_id )
        return

    def _make_response( request, log_id ):
        """ Takes request;
                examines session['authz_info'];
                returns a response object to caller.
            Called by login(). """
        log.info( u'in views._make_response(); id, %s; starting' % log_id )
        if request.session['authz_info']['authorized'] == True:
            if 'next' in request.GET:
              response = HttpResponseRedirect( request.GET['next'] )
            else:
                redirect_url = u'%s://%s%s' % (
                    request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'search_url',) )
            response = HttpResponseRedirect( redirect_url )
        else:
            response = HttpResponseForbidden( '403 / Forbidden; unauthorized user' )
        return response
    ## init
    log_id = common.get_log_identifier( request.session )
    log.info( u'in login(); id, %s; starting' % log_id )
    request.session['authz_info'] = { 'authorized': False }
    ## checks
    if _check_shib( request, log_id ) == False:
        _check_dev_auth_hack( request, log_id )
    ## response
    response = _make_response( request, log_id )
    return response



## logout ##

def logout( request ):
    """ Removes session-based authentication. """
    log.info( u'in logout(); starting' )
    request.session[u'authz_info'] = { u'authorized': False }
    django_logout( request )
    if u'next' in request.GET:
        redirect_url = request.GET[u'next']
    else:
        redirect_url = u'%s://%s%s' % (
            request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'search_url',) )
    return HttpResponseRedirect( redirect_url )


## view_xml ##

def view_xml( request, inscription_id ):
    """ Returns inscription-xml from github lookup. """
    xml_prepper = XmlPrepper()
    ## lookup xml
    # xml_url = '%s/%s.xml' % ( unicode(os.environ['IIP_SEARCH__XML_DIR_URL']), inscription_id )
    xml_url = '%s/%s.xml' % ( settings_app.IIP_SMR__XML_DIR_URL, inscription_id )
    lookup_headers = xml_prepper.prep_lookup_headers( request.META )
    lookup_response = requests.get( xml_url, headers=lookup_headers )  # eventually maybe offload this to helper class for a try/except to handle github's periodic downtime
    ## prep response
    response = HttpResponse()
    enhanced_response = xml_prepper.enhance_response( response, lookup_response )
    return enhanced_response


## static pages ##

def info( request, info_id ):
    """ Displays requested static page. """
    info_page = get_object_or_404( StaticPage, slug=info_id )
    context_dct = {
        'html_content': info_page.content,
        'title_header': info_page.title_header,
        'title': info_page.title
        }
    return render( request, u'iip_search_templates/static.html', context_dct )

def edit_info( request ):
    """ If logged in, takes user to static-pages admin. """
    if 'authz_info' not in request.session.keys() or 'authorized' not in request.session[u'authz_info'].keys() or request.session[u'authz_info'][u'authorized'] == False:
        return HttpResponseForbidden( '403 / Forbidden' )
    user = authenticate( username=settings_app.DB_USER, password=settings_app.DB_USER_PASSWORD )
    django_login( request, user )
    url = reverse( 'admin:iip_smr_web_app_staticpage_changelist' )
    return HttpResponseRedirect( url )
