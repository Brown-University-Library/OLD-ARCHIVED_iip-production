# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to


urlpatterns = patterns('',

    url( r'^login/$',  'iip_search_app.views.login', name=u'login_url' ),
    url( r'^logout/$',  'iip_search_app.views.logout', name=u'logout_url' ),

    url( r'^results/$',  'iip_search_app.views.results', name=u'results_url' ),

    url( r'^search/$',  'iip_search_app.views.results', name=u'search_url' ),

    url( r'^api/$', 'iip_search_app.views.api_wrapper', name=u"api_wrapper"),

    url( r'^viewinscr/(?P<inscrid>.*)/$', 'iip_search_app.views.viewinscr', name='inscription_url'),

    url( r'^view_xml/(?P<inscription_id>.*)/$', 'iip_search_app.views.view_xml', name=u'xml_url' ),

    url( r'^info/(?P<info_id>.*)/$', 'iip_search_app.views.info', name=u'info_url' ),
    url( r'^edit_info/$', 'iip_search_app.views.edit_info', name=u'edit_info_url' ),

    url( r'^$', redirect_to, {'url': 'search/'} ),

    )
