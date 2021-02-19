# -*- coding: utf-8 -*-

import csv, datetime, json, logging, os, pprint, re
import urllib.request

import requests, solr
from .models import StaticPage, StoryPage
from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, render_to_response
from iip_smr_web_app import common, models, settings_app
from iip_smr_web_app import forms
from iip_smr_web_app import old_forms
from iip_smr_web_app.libs import ajax_snippet
from iip_smr_web_app.libs.proxy_helper import rewrite
from iip_smr_web_app.libs.version_helper import Versioner
from iip_smr_web_app.libs.view_xml_helper import XmlPrepper
from iip_smr_web_app.libs.wordlist.wordlist import get_latin_words_pos, get_latin_words_pos_new, get_doubletree_data


log = logging.getLogger(__name__)
versioner = Versioner()



def wordlist(request, language=None):
    words = {}
    data = {}
    if language == 'latin':
        wordlist_data = get_latin_words_pos_new()
        words = wordlist_data["lemmas"]
        data = wordlist_data["db_list"]
    elif language == 'greek':  # todo
        pass
    else:  # 'hebrew'; todo
        pass
    context = {"words": words, "doubletree_data": json.dumps(data), 'language': language}
    return render(request, "wordlist/wordlist_root.html", context)


## proxy start ##

def proxy( request, slug=None ):
    """ Handles resources/labs/etc urls """
    log.debug( 'slug, `%s`' % slug )
    log.debug( 'request.__dict__, ```%s```' % pprint.pformat(request.__dict__) )
    gets = request.GET
    log.debug( 'gets, `%s`' % gets )
    fetch_url = settings_app.FETCH_DIR_URL  # includes trailing slash
    proxy_url = reverse( 'proxy_url' )  # includes trailing slash
    log.debug( 'proxy_url, `%s`' % proxy_url )
    js_rewrite_url = '%s%s' % ( fetch_url, 'doubletreejs/' )
    if slug:
        fetch_url = '%s%s' % ( fetch_url, urllib.parse.unquote_plus(slug) )
    if gets:
        r = requests.get( fetch_url, params=gets )
    else:
        r = requests.get( fetch_url )
    log.debug( 'r.url, ```%s```' % r.url )
    raw = r.content.decode( 'utf-8' )
    log.debug( 'raw, ```%s```' % raw )

    rewritten = rewrite( raw, proxy_url, js_rewrite_url )

    # rewritten = raw.replace(
    #     'href="../', 'href="%s' % proxy_url )
    # rewritten = rewritten.replace(
    #     '<script src="doubletreejs/', '<script src="%s' % js_rewrite_url )
    # rewritten = rewritten.replace(
    #     'textRequest.open("GET", "doubletree-data.txt"', 'textRequest.open("GET", "%sdoubletree-data.txt"' % proxy_url )
    # rewritten = rewritten.replace(
    #     'src="../index_search.js"', 'src="http://127.0.0.1:8000/resources/word_labs/index_search.js/"' )
    # rewritten = rewritten.replace(
    #     'src="../levenshtein.min.js"', 'src="http://127.0.0.1:8000/resources/word_labs/levenshtein.min.js/"' )
    # rewritten = rewritten.replace(
    #     '<!DOCTYPE HTML>', '' )
    # rewritten = rewritten.replace(
    #     '<html>', '', 2 )

    # log.debug( 'rewritten, ```%s```' % rewritten )
    if request.META['PATH_INFO'][-5:] == '.xml/':
        resp = HttpResponse( rewritten, content_type='application/xml; charset=utf-8' )
    elif request.META['PATH_INFO'][-5:] == '.css/':
        resp = HttpResponse( rewritten, content_type='text/css; charset=utf-8' )
    elif request.META['PATH_INFO'][-4:] == '.js/':
        resp = HttpResponse( rewritten, content_type='application/javascript; charset=utf-8' )
    else:
        # resp = HttpResponse( rewritten )
        context = {
            'title': 'Word Labs -- under active development',
            'html_content': rewritten }
        resp = render( request, 'resources/proxy.html', context )
    return resp

def proxy_doubletree( request ):
    log.debug( 'starting' )
    url = '%s%s' % ( settings_app.FETCH_DIR_URL, 'doubletree-data.txt' )
    r = requests.get( url )
    return HttpResponse( r.content )

## proxy end ##


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
        # form = forms.SearchForm()  # an unbound form
        form = forms.SearchForm({'type_':'or', 'physical_type_':'or', 'language_':'or', 'religion_':'or', 'material_':'or'})  # an unbound form
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

    ## view starts here

    log_id = common.get_log_identifier( request.session )
    log.info( 'id, `%s`; starting views.results()' % log_id )
    if not u'authz_info' in request.session:
        request.session[u'authz_info'] = { u'authorized': False }

    if request.method == u'POST': # form has been submitted by user
        log.debug( 'POST, search-form was submitted by user' )
        request.encoding = u'utf-8'
        form = forms.SearchForm(request.POST)
        if not form.is_valid():
            log.debug( 'form not valid, redirecting')
            redirect_url = '%s://%s%s?q=*:*' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse('mapsearch_url') )
            log.debug( 'redirect_url for non-valid form, ```%s```' % redirect_url )
            return HttpResponseRedirect( redirect_url )
        qstring = form.generateSolrQuery()
        if qstring == '':
            qstring = '*'
        log.debug( f'qstring, ```{qstring}```' )
        redirect_url = '%s://%s%s?q=%s' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse('mapsearch_url'), qstring )
        log.debug( 'redirect_url for valid form, ```%s```' % redirect_url )
        return HttpResponseRedirect( redirect_url )

    if request.method == 'GET' and request.GET.get('q', None) != None:
        log.debug( 'GET, with params, hit solr and show results' )
        context_dct = _get_results_context(request, log_id)

        # log.debug( f'context_dct-iipResult, ```{context_dct["iipResult"]}```' )  # solr.paginator.SolrPage -- <https://github.com/search5/solrpy/>
        iipResult_dct = {}
        iipResult_page_lst = []
        iipResult_count = 0
        if context_dct['iipResult']:  # will be '' if no results are found
            iipResult_dct = context_dct['iipResult'].result
            iipResult_page_lst = context_dct["iipResult"].paginator.page_range
            iipResult_count = context_dct["iipResult"].paginator.count
        context_dct['iipResult'] = iipResult_dct
        context_dct['pages'] = iipResult_page_lst
        context_dct['results_count'] = iipResult_count

        if request.GET.get('format', '') == 'json':
            log.debug( 'returning json' )
            resp = HttpResponse( json.dumps(context_dct, sort_keys=True, indent=2), content_type='application/javascript; charset=utf-8' )
        else:
            resp = render( request, 'iip_search_templates/results_dev.html', context_dct )
        return resp
    elif request.is_ajax():  # user has requested another page, a facet, etc.
        log.debug( 'request.is_axax() is True' )
        return HttpResponse( _get_ajax_unistring(request) )
    else:  # regular GET, no params
        log.debug( 'GET, no params, show search form' )
        return render( request, u'mapsearch/mapsearch.html', _get_searchform_context(request, log_id) )

    # if request.method == 'GET' and request.GET.get('q', None) != None:
    #     log.debug( 'GET, with params, hit solr and show results' )
    #     context_dct = _get_results_context(request, log_id)

    #     # log.debug( f'context_dct-iipResult, ```{context_dct["iipResult"]}```' )  # solr.paginator.SolrPage -- <https://github.com/search5/solrpy/>
    #     iipResult_dct = context_dct['iipResult'].result
    #     iipResult_page_lst = context_dct["iipResult"].paginator.page_range
    #     iipResult_count = context_dct["iipResult"].paginator.count
    #     context_dct['iipResult'] = iipResult_dct
    #     context_dct['pages'] = iipResult_page_lst
    #     context_dct['results_count'] = iipResult_count

    #     if request.GET.get('format', '') == 'json':
    #         log.debug( 'returning json' )
    #         resp = HttpResponse( json.dumps(context_dct, sort_keys=True, indent=2), content_type='application/javascript; charset=utf-8' )
    #     else:
    #         resp = render( request, 'iip_search_templates/results_dev.html', context_dct )
    #     return resp
    # elif request.is_ajax():  # user has requested another page, a facet, etc.
    #     log.debug( 'request.is_axax() is True' )
    #     return HttpResponse( _get_ajax_unistring(request) )
    # else:  # regular GET, no params
    #     log.debug( 'GET, no params, show search form' )
    #     return render( request, u'mapsearch/mapsearch.html', _get_searchform_context(request, log_id) )

    ## end def results()


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
        image_caption: list = q.results[0].get( 'image-caption', None )
        log.debug( f'image_caption, ```{image_caption}```' )
        if image_caption:
            image_caption = image_caption[0]

        view_xml_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'xml_url', kwargs={u'inscription_id':inscrid})  )
        current_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'inscription_url', kwargs={u'inscrid':inscrid})  )
        return ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url, image_caption )

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

        #query solr instance wrong
        #is it solr instance wrong or the view code?
    def _call_viewinsc_solr( inscription_id ):
        """ Hits solr with inscription-id.
                Returns a solrpy response-object, where `q.results` is a list of dicts.
            Called by _prepare_viewinscr_get_data(). """
        s = solr.SolrConnection( settings_app.SOLR_URL )
        log.debug( f'settings_app.SOLR_URL, ```{settings_app.SOLR_URL}```' )
        qstring = u'inscription_id:%s' % inscription_id
        try:
            q = s.query(qstring)
        except:
            q = s.query('*:*', **args)
        log.debug( f'q, ``{pprint.pformat(q.__dict__)}``' )
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
            'view_xml_url': view_xml_url,
            }
        return_str = ajax_snippet.render_block_to_string( 'iip_search_templates/viewinscr.html', 'viewinscr', context )
        return_response = HttpResponse( return_str )
        return return_response

    def _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id, image_caption ):
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
            'image_url':  "https://github.com/Brown-University-Library/iip-images/raw/master/" + inscrid + ".jpg",
            'image_caption': image_caption
            }
        log.debug( f'context, ```{pprint.pformat(context)}```' )
        return_response = render( request, u'iip_search_templates/viewinscr.html', context )
        return return_response

    log_id = _setup_viewinscr( request )
    log.info( u'in viewinscr(); id, %s; starting' % log_id )
    ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url, image_caption ) = _prepare_viewinscr_get_data( request, inscrid )
    if request.is_ajax():
        log.debug( 'ajax-request' )
        return_response = _prepare_viewinscr_ajax_get_response( q, z_bibids, specific_sources, view_xml_url )
    else:
        log.debug( 'non-ajax-request' )
        return_response = _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id, image_caption )
    return return_response


## api ##

def api_wrapper( request ):
    old_params = dict(request.GET)
    params = dict([(x.replace('.', '_'), old_params[x] if len(old_params[x]) > 1 else old_params[x][0]) for x in old_params])
    params['wt'] = 'json'
    if('q' in params and params['q']): params['q'] += " AND display_status:approved"
    s = solr.SolrConnection( settings_app.SOLR_URL )

    r = s.raw_query(**params)
    log.debug( f'type(r), ``{type(r)}``' )

    unicode_r = r.decode( 'utf-8' )
    log.debug( f'type(unicode_r), ``{type(unicode_r)}``' )

    # resp = HttpResponse( str(r), content_type="application/json" )
    resp = HttpResponse( unicode_r, content_type='application/javascript; charset=utf-8' )
    resp['Access-Control-Allow-Origin'] = "*"

    return resp

    # resp = HttpResponse( json.dumps(context, sort_keys=True, indent=2), content_type='application/javascript; charset=utf-8' )


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
                    request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'mapsearch_url',) )
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
            request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'mapsearch_url',) )
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


def version( request ):
    """ Displays branch and commit for easy comparison between localdev, dev, and production web-apps. """
    rq_now = datetime.datetime.now()
    commit = versioner.get_commit()
    branch = versioner.get_branch()
    info_txt = commit.replace( 'commit', branch )
    resp_now = datetime.datetime.now()
    taken = resp_now - rq_now
    context_dct = versioner.make_context( request, rq_now, info_txt, taken )
    output = json.dumps( context_dct, sort_keys=True, indent=2 )
    return HttpResponse( output, content_type='application/json; charset=utf-8' )


## static pages ##

def info( request, info_id ):
    """ Displays requested 'about' static page. """
    info_page = get_object_or_404( StaticPage, slug=info_id )
    context_dct = {
        'html_content': info_page.content,
        'title_header': info_page.title_header,
        'title': info_page.title
        }
    return render( request, u'iip_search_templates/static.html', context_dct )

def resources_general( request, info_id ):
    """ Displays requested 'resources' static page. """
    info_page = get_object_or_404( StaticPage, slug=info_id )
    context_dct = {
        'html_content': info_page.content,
        'title_header': info_page.title_header,
        'title': info_page.title
        }
    log.debug( 'context_dct, ```%s```' % pprint.pformat(context_dct) )
    return render( request, u'iip_search_templates/static.html', context_dct )

def edit_info( request ):
    """ If logged in, takes user to static-pages admin. """
    if 'authz_info' not in request.session.keys() or 'authorized' not in request.session[u'authz_info'].keys() or request.session[u'authz_info'][u'authorized'] == False:
        return HttpResponseForbidden( '403 / Forbidden' )
    user = authenticate( username=settings_app.DB_USER, password=settings_app.DB_USER_PASSWORD )
    django_login( request, user )
    url = reverse( 'admin:iip_smr_web_app_staticpage_changelist' )
    return HttpResponseRedirect( url )



###SAM
# def about(request):
#     return render(request, 'about/about.html')


def why_inscription(request):
    return render(request, 'about/why_inscription.html')

def project_description(request):
    return render(request, 'about/project_description.html')

def documentation(request):
    return render(request, 'about/documentation.html')

def api(request):
    return render(request, 'about/api.html')

def funding(request):
    return render(request, 'about/funding.html')

def team(request):
    return render(request, 'about/team.html')

def copyright(request):
    return render(request, 'about/copyright.html')


def index(request):
    return stories(request, index_page=True)


def contact(request):
    return render(request, 'contact/contact.html')

def mapsearch(request):
    return render(request, 'mapsearch/mapsearch.html')


def resources(request):
    return render(request, 'resources/resources.html')

def bibliography(request):
    return render(request, 'resources/bibliography.html')


def timeline(request):
    return render(request, 'resources/timeline.html')


def guide_to_searching(request):
    return render(request, 'resources/guide_to_searching.html')

def glossary(request):
    return render(request, 'resources/glossary.html')

def conventional_transcription_symbols(request):
    return render(request, 'resources/conventional_transcription_symbols.html')


def load_layers(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    log.debug( f'BASE_DIR, ```{BASE_DIR}```' )

    json_data = os.path.join(BASE_DIR, 'iip_smr_web_app/static/', "mapsearch/geoJSON/roman_provinces.geojson")
    data = open(json_data, 'r')
    roman_provinces = json.load(data)
    roman_provinces = json.dumps(roman_provinces)
    data.close()

    json_data = os.path.join(BASE_DIR, 'iip_smr_web_app/static/', "mapsearch/geoJSON/roman_roads.geojson")
    data = open(json_data, 'r')
    roman_roads = json.load(data)
    roman_roads = json.dumps(roman_roads)
    data.close()

    json_data = os.path.join(BASE_DIR, 'iip_smr_web_app/static/', "mapsearch/geoJSON/byzantine_provinces_400CE.geojson")
    data = open(json_data, 'r')
    byzantine = json.load(data)
    byzantine = json.dumps(byzantine)
    data.close()

    json_data = os.path.join(BASE_DIR, 'iip_smr_web_app/static/', "mapsearch/geoJSON/IIP_regions.geojson")
    data = open(json_data, 'r')
    iip = json.load(data)
    iip = json.dumps(iip)
    data.close()

    json_data = os.path.join(BASE_DIR, 'iip_smr_web_app/static/', "mapsearch/geoJSON/king_herod_boundaries_37BCE.geojson")
    data = open(json_data, 'r')
    king_herod = json.load(data)
    king_herod = json.dumps(king_herod)
    data.close()

    context = {'roman_provinces':roman_provinces, 'roman_roads':roman_roads, 'byzantine_provinces_400CE': byzantine, 'iip_regions': iip, 'king_herod': king_herod}

    dump = json.dumps(context)
    return HttpResponse(dump, content_type='application/json')



def stories(request, index_page=False):
    story_page = StoryPage.objects.all()

    slug = []
    title_header = []
    title = []
    author = []
    date = []
    short_summary = []
    thumbnail_intro = []
    thumbnail_image_url = []
    content = []
    relevant_inscription_id = []

    # image = []

    for el in story_page:
        slug.append(el.slug)
        title_header.append(el.title_header)
        title.append(el.title)
        author.append(el.author)
        date.append(el.date)
        short_summary.append(el.short_summary)
        thumbnail_intro.append(el.thumbnail_intro)
        thumbnail_image_url.append(el.thumbnail_image_url)
        content.append(el.content)
        relevant_inscription_id.append(el.relevant_inscription_id)

        # image.append(el.image)


    context = {
        'slug': slug,
        'title_header': title_header,
        'title': title,
        'author': author,
        'story_date': date,
        'short_summary': short_summary,
        'thumbnail_intro': thumbnail_intro,
        'thumbnail_image_url': thumbnail_image_url,
        'content': content,
        'relevant_inscription_id': relevant_inscription_id,
        'num_stories': range(len(story_page)),

        # 'image': image
    }

    if index_page:
        return render(request, 'index/index.html', context)
    else:
        return render(request, 'stories/stories.html', context)


def individual_story(request, story_id):
    story_page = get_object_or_404( StoryPage, slug=story_id)

    inscription_id = []
    languages = []
    date = []
    place_found = []
    transcription = []
    translation = []
    dimension = []
    date_start = []
    date_end = []
    num_relevantInscriptions = 0
    image_url = []


    for item in story_page.relevant_inscription_id.split(','):
        num_relevantInscriptions += 1
        url = 'https://library.brown.edu/search/solr_pub/iip/?start=0&rows=100&indent=on&wt=json&q=inscription_id%3A%22' + item.lower() + '%22'

        with urllib.request.urlopen(url) as response:
            inscription_boolean = False
            s = response.read()
            encoding = response.info().get_content_charset('utf-8')
            data = json.loads(s.decode(encoding))

            try:
                inscription_id.append(data["response"]["docs"][0]["inscription_id"])


                languages.append(data["response"]["docs"][0]["language_display"])
                date.append(data["response"]["docs"][0]["date_desc"])
                place_found.append(data["response"]["docs"][0]["place_found"])
                transcription.append(data["response"]["docs"][0]["transcription"])
                translation.append(data["response"]["docs"][0]["translation"])
                dimension.append(data["response"]["docs"][0]["dimensions"])
                if "notBefore" in data["response"]["docs"][0]:
                    date_start.append(data["response"]["docs"][0]["notBefore"])
                else:
                    date_start.append('Unknown')
                date_end.append(data["response"]["docs"][0]["notAfter"])
                image_url.append("https://github.com/Brown-University-Library/iip-images/raw/master/" + str(data["response"]["docs"][0]["inscription_id"]) + ".jpg")
                inscription_boolean = True
            except:
                log.debug( 'No Relevant Inscriptions' )

    context = {
        'slug': story_page.slug,
        'title_header': story_page.title_header,
        'title': story_page.title,
        'author': story_page.author,
        'story_date': story_page.date,
        'short_summary': story_page.short_summary,
        'content': story_page.content,
        'relevant_inscription_id': story_page.relevant_inscription_id,
        'current_url': request.build_absolute_uri,
        'image_url': image_url,
        }

    if inscription_boolean:
        context["inscription_id"] = inscription_id
        context["languages"] = languages
        context["date"] = date
        context["place_found"] = place_found
        context["transcription"] = transcription
        context["translation"] = translation
        context["dimension"] = dimension
        context["date_start"] = date_start
        context["date_end"] = date_end
        context["num_relevantInscriptions"] = range(num_relevantInscriptions)


    return render(request, 'stories/individual_story.html', context)




###ENDSAM




























































































































































































#### Old search function (needs its unique url i.e. /results/[OLD]/?q=*)

# def old_results( request ):
#     """ Handles /results/ GET, POST, and ajax-GET. """
#     def _get_results_context( request, log_id ):
#         """ Returns correct context for POST.
#             Called by results() """
#         log.debug( 'starting' )
#         context = {}
#         request.encoding = u'utf-8'

#         form = old_forms.SearchForm( request.POST )  # form bound to the POST data

#         resultsPage = 1
#         qstring_provided = None
#         if request.method == u'GET':
#             qstring_provided = request.GET.get("q", None)
#             resultsPage = int(request.GET.get('resultsPage', resultsPage))

#         if form.is_valid() or qstring_provided:
#             initial_qstring = ""
#             if qstring_provided:
#                 initial_qstring = qstring_provided
#             else:
#                 initial_qstring = form.generateSolrQuery()

#             updated_qstring = common.updateQstring(
#                 initial_qstring=initial_qstring, session_authz_dict=request.session['authz_info'], log_id=common.get_log_identifier(request.session) )['modified_qstring']
#             context = common.paginateRequest( qstring=updated_qstring, resultsPage=resultsPage, log_id=common.get_log_identifier(request.session) )
#             log.debug( 'context, ```%s```' % pprint.pformat(context) )
#             context[u'session_authz_info'] = request.session[u'authz_info']
#             context[u'admin_links'] = common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id )
#             context[u'initial_qstring'] = initial_qstring
#         log.debug( 'context.keys(), ```%s```' % pprint.pformat(sorted(context.keys())) )
#         log.debug( 'type(context), `%s`' % type(context) )



#         # results = context['iipResult']
#         # log.debug( 'type(results), `%s`' % type(results) )
#         # for (i, result) in enumerate(results.object_list):
#         #     log.debug( 'type(result), `%s`' % type(result) )
#         #     log.debug( 'result, `%s`' % result )
#         #     if i > 0:
#         #         break
#         #     1/0


#         return context

#     def _get_ajax_unistring( request ):
#         """ Returns unicode string based on ajax update.
#             Called by results() """
#         log_id = common.get_log_identifier(request.session)
#         log.info( 'id, `%s`; starting' % log_id )
#         initial_qstring = request.GET.get( u'qstring', u'*:*' )
#         updated_qstring = common.updateQstring( initial_qstring, request.session[u'authz_info'], log_id )[u'modified_qstring']
#         resultsPage = int( request.GET[u'resultsPage'] )
#         context = common.paginateRequest(
#             qstring=updated_qstring, resultsPage=resultsPage, log_id=log_id )
#         return_str = ajax_snippet.render_block_to_string(u'iip_search_templates/old_results.html', u'content', context)
#         return unicode( return_str )

#     def _get_searchform_context( request, log_id ):
#         """ Returns correct context for GET.
#             Called by results() """
#         log.debug( '_get_searchform_context() starting' )
#         if not u'authz_info' in request.session:
#             request.session[u'authz_info'] = { u'authorized': False }
#         # form = SearchForm()  # an unbound form
#         form = old_forms.SearchForm()  # an unbound form
#         log.debug( 'form, `%s`' % repr(form) )
#         # place_field_object = form.fields['place']
#         # place_field_object.choices = [(item, item) for item in sorted( common.facetResults('placeMenu').keys()) if item]
#         # form.fields['place'] = place_field_object
#         context = {
#             u'form': form,
#             u'session_authz_info': request.session[u'authz_info'],
#             u'settings_app': settings_app,
#             u'admin_links': common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id )
#             }
#         log.debug( 'context, ```%s```' % pprint.pformat(context) )
#         return context
#     log_id = common.get_log_identifier( request.session )
#     log.info( 'id, `%s`; starting' % log_id )
#     if not u'authz_info' in request.session:
#         request.session[u'authz_info'] = { u'authorized': False }
#     if request.method == u'POST': # form has been submitted by user
#         log.debug( 'POST, search-form was submitted by user' )
#         request.encoding = u'utf-8'
#         form = old_forms.SearchForm(request.POST)
#         if not form.is_valid():
#             log.debug( 'form not valid, redirecting')
#             redirect_url = '%s://%s%s?q=*:*' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'results_url') )
#             log.debug( 'redirect_url for non-valid form, ```%s```' % redirect_url )
#             return HttpResponseRedirect( redirect_url )
#         qstring = form.generateSolrQuery()
#         # e.g. http://library.brown.edu/cds/projects/iip/results?q=*:*
#         redirect_url = '%s://%s%s?q=%s' % ( request.META[u'wsgi.url_scheme'], request.get_host(), reverse(u'results_url'), qstring )
#         log.debug( 'redirect_url for valid form, ```%s```' % redirect_url )
#         return HttpResponseRedirect( redirect_url )
#     if request.method == u'GET' and request.GET.get(u'q', None) != None:
#         log.debug( 'GET, with params, hit solr and show results' )
#         return render( request, u'iip_search_templates/old_results.html', _get_results_context(request, log_id) )
#     elif request.is_ajax():  # user has requested another page, a facet, etc.
#         log.debug( 'request.is_axax() is True' )
#         return HttpResponse( _get_ajax_unistring(request) )
#     else:  # regular GET, no params
#         log.debug( 'GET, no params, show search form' )
#         return render( request, u'iip_search_templates/search_form.html', _get_searchform_context(request, log_id) )



# ## view inscription ##

# old_biblRegex = re.compile(r'bibl=(.*)\.xml\|nType=(.*)\|n=(.*)')

# def old_viewinscr(request, inscrid):
#     """ Handles view-inscription GET with new Javascript and Zotero bibliography. """

#     def _bib_tuple_or_none(s):
#         t = old_biblRegex.match(s)
#         if t:
#             return t.groups()
#         elif s == "ms":
#             return ("ms", None, None)
#         else:
#             return None

#     # Prepare an inscription
#     def _prepare_viewinscr_get_data (request, inscrid):
#         """ Prepares data for regular or ajax GET.
#                 Returns a tuple of vars.
#             Called by viewinscr(). """
#         log.debug( u'in _prepare_viewinscr_get_data(); starting' )
#         log_id = common.get_log_identifier( request.session )
#         q = _call_viewinsc_solr( inscrid )  # The results of the solr query to find the inscription. q.results is list of dictionaries of values.
#         current_display_status = _update_viewinscr_display_status( request, q )
#         z_bibids_initial = [_bib_tuple_or_none(x) for x in q.results[0]['bibl']]
#         z_bibids = {}
#         log.debug( f'z_bibids_initial, ```{z_bibids_initial}```' )
#         for entry in z_bibids_initial:
#             if not entry:
#                 continue
#             bibid, ntype, n = entry
#             if(not bibid in z_bibids):
#                 z_bibids[bibid] = []
#             if(not (ntype, n) in z_bibids[bibid]):
#                 #append ntype
#                 z_bibids[bibid].append((ntype, n))
#         specific_sources = dict()
#         specific_sources['transcription'] = _bib_tuple_or_none(q.results[0]['biblTranscription'][0]) if 'biblTranscription' in q.results[0] else ""
#         specific_sources['translation'] = _bib_tuple_or_none(q.results[0]['biblTranslation'][0]) if 'biblTranslation' in q.results[0] else ""
#         specific_sources['diplomatic'] = _bib_tuple_or_none(q.results[0]['biblDiplomatic'][0]) if 'biblDiplomatic' in q.results[0] else ""

#         view_xml_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'xml_url', kwargs={u'inscription_id':inscrid})  )
#         current_url = u'%s://%s%s' % (  request.META[u'wsgi.url_scheme'],  request.get_host(),  reverse(u'inscription_url', kwargs={u'inscrid':inscrid})  )
#         return ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url )

#     def _setup_viewinscr( request ):
#         """ Takes request;
#                 updates session with authz_info and log_id;
#                 returns log_id.
#             Called by viewinscr() """
#         log.debug( u'in _setup_viewinscr(); starting' )
#         if not u'authz_info' in request.session:
#             request.session[u'authz_info'] = { u'authorized': False }
#         log_id = common.get_log_identifier( request.session )
#         return log_id

#     def _call_viewinsc_solr( inscription_id ):
#         """ Hits solr with inscription-id.
#                 Returns a solrpy query-object.
#             Called by _prepare_viewinscr_get_data(). """
#         s = solr.SolrConnection( settings_app.SOLR_URL )
#         qstring = u'inscription_id:%s' % inscription_id
#         try:
#             q = s.query(qstring)
#         except:
#             q = s.query('*:*', **args)
#         return q

#     def _update_viewinscr_display_status( request, q ):
#         """ Takes request and solrypy query object.
#                 Updates session  display-status.
#                 Returns current display-status.
#             Called by _prepare_viewinscr_get_data(). """
#         current_display_status = u'init'
#         if int( q.numFound ) > 0:
#             current_display_status = q.results[0]['display_status']
#             request.session['current_display_status'] = current_display_status
#         return current_display_status

#     def _prepare_viewinscr_ajax_get_response( q, z_bibids, specific_sources, view_xml_url ):
#         """ Returns view-inscription response-object for ajax GET.
#             Called by viewinscr() """
#         log.debug( u'in _prepare_viewinscr_ajax_get_response(); starting' )
#         context = {
#             'inscription': q,
#             'z_ids': z_bibids,
#             'biblDiplomatic' : specific_sources['diplomatic'],
#             'biblTranscription' : specific_sources['transcription'],
#             'biblTranslation' : specific_sources['translation'],
#             'biblioFull': False,
#             'view_xml_url': view_xml_url }
#         log.debug( f'z_bibids, ```{z_bibids}```' )
#         return_str = ajax_snippet.render_block_to_string( 'iip_search_templates/old_viewinscr.html', 'viewinscr', context )
#         return_response = HttpResponse( return_str )
#         return return_response

#     def _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id ):
#         """ Returns view-inscription response-object for regular GET.
#             Called by viewinscr() """
#         log.debug( u'in _prepare_viewinscr_plain_get_response(); starting' )
#         context = {
#             'inscription': q,
#             'z_ids': z_bibids,
#             'biblDiplomatic' : specific_sources['diplomatic'],
#             'biblTranscription' : specific_sources['transcription'],
#             'biblTranslation' : specific_sources['translation'],
#             'biblioFull': True,
#             'chosen_display_status': current_display_status,
#             'inscription_id': inscrid,
#             'session_authz_info': request.session['authz_info'],
#             'admin_links': common.make_admin_links( session_authz_dict=request.session[u'authz_info'], url_host=request.get_host(), log_id=log_id ),
#             'view_xml_url': view_xml_url,
#             'current_url': current_url,
#             }
#         # log.debug( u'in _prepare_viewinscr_plain_get_response(); context, %s' % pprint.pformat(context) )
#         return_response = render( request, u'iip_search_templates/old_viewinscr.html', context )
#         return return_response

#     log_id = _setup_viewinscr( request )
#     log.info( u'in viewinscr(); id, %s; starting' % log_id )
#     ( q, z_bibids, specific_sources, current_display_status, view_xml_url, current_url ) = _prepare_viewinscr_get_data( request, inscrid )
#     if request.is_ajax():
#         return_response = _prepare_viewinscr_ajax_get_response( q, z_bibids, specific_sources, view_xml_url )
#     else:
#         return_response = _prepare_viewinscr_plain_get_response( q, z_bibids, specific_sources, current_display_status, inscrid, request, view_xml_url, current_url, log_id )
#     return return_response
