# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from iip_smr_web_app import views


admin.autodiscover()

urlpatterns = [

    url(r'^wordlist/$', views.wordlist, name='wordslist_url'),
    url(r'^wordlist/(?P<language>.*)/$', views.wordlist, name='wordslist_url'),

    url(r'^admin/', include(admin.site.urls)),
    url( r'^login/$',  views.login, name='login_url' ),
    url( r'^logout/$',  views.logout, name='logout_url' ),
    # url( r'^old_search/$',  views.old_results, name='oldsearch_url' ),
    url( r'^api/$', views.api_wrapper, name='api_wrapper' ),
    url( r'^viewinscr/(?P<inscrid>.*)/$', views.viewinscr, name='inscription_url'),
    url( r'^view_xml/(?P<inscription_id>.*)/$', views.view_xml, name='xml_url' ),

    # url( r'^info/(?P<info_id>.*)/$', views.info, name='info_url' ),
    url( r'^info/$',  views.version, name='version_url' ),
    url( r'^version/$',  views.version, name='version_url' ),

    url( r'^results/$',  views.results, name='results_url' ),

    url(r'^mapsearch/$', views.results, name='mapsearch_url' ),
    url(r'^mapsearch/load_layers/$', views.load_layers, name='load_layers'),

    url( r'^$',  RedirectView.as_view(pattern_name='mapsearch_url') ),

    ]
