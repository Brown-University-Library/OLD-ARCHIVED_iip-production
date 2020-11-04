# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from iip_smr_web_app import views


admin.autodiscover()

urlpatterns = [

    url(r'^wordlist/$', views.wordlist, name='wordslist_url'),
    url(r'^wordlist/new_latin_data$', views.wordlist_new, name='wordslist_url_new'),
    url(r'^wordlist/old_latin_data$', views.wordlist_old, name='wordslist_url_old'),
    url(r'^wordlist/latinword/doubletree/(?P<lemma>.*)/(?P<pos>.*)/$', views.latin_doubletree, name='latin_doubletree_url'),

    url(r'^admin/', include(admin.site.urls)),
    url( r'^login/$',  views.login, name='login_url' ),
    url( r'^logout/$',  views.logout, name='logout_url' ),
    # url( r'^old_search/$',  views.old_results, name='oldsearch_url' ),
    url( r'^api/$', views.api_wrapper, name='api_wrapper' ),
    url( r'^viewinscr/(?P<inscrid>.*)/$', views.viewinscr, name='inscription_url'),
    url( r'^view_xml/(?P<inscription_id>.*)/$', views.view_xml, name='xml_url' ),

    # url( r'^info/(?P<info_id>.*)/$', views.info, name='info_url' ),
    url( r'^info/$',  views.version, name='version_url' ),

    url( r'^about/(?P<info_id>.*)/$', views.info, name='info_url' ),

    url( r'^resources/word_labs/$', views.proxy, name='proxy_url' ),
    url( r'^presources/word_labs/doubletree-data.txt/$', views.proxy_doubletree, name='proxy_doubletree_url' ),
    url( r'^resources/word_labs/(?P<slug>.*)/$', views.proxy, name='proxy_param_url' ),

    url( r'^resources/(?P<info_id>.*)/$', views.resources_general, name='resources_general_url' ),

    url( r'^edit_info/$', views.edit_info, name='edit_info_url' ),
    url( r'^results/$',  views.results, name='results_url' ),

    ##NEW
    url(r'^about/$', views.why_inscription,  name='about_url' ),
    url(r'^about/why_inscription/$', views.why_inscription,  name='why_inscription_url' ),
    url(r'^about/project_description/$', views.project_description,  name='project_description_url' ),
    url(r'^about/documentation/$', views.documentation,  name='documentation_url' ),
    url(r'^about/api/$', views.api,  name='api_url' ),
    url(r'^about/funding/$', views.funding,  name='funding_url' ),
    url(r'^about/team/$', views.team,  name='team_url' ),
    url(r'^about/copyright/$', views.copyright,  name='copyright_url' ),

    url(r'^index/$', views.index, name='index_url' ),

    url(r'^contact/$', views.contact, name='contact_url' ),

    url(r'^mapsearch/$', views.results, name='mapsearch_url' ),
    url(r'^mapsearch/load_layers/$', views.load_layers, name='load_layers'),

    url(r'^resources/$', views.bibliography, name='resources_url' ),
    url(r'^resources/bibliography/$', views.bibliography, name='bibliography_url' ),
    url(r'^resources/timeline/$', views.timeline, name='timeline_url' ),
    url(r'^resources/guide_to_searching/$', views.guide_to_searching, name='guide_to_searching_url' ),
    url(r'^resources/glossary/$', views.glossary, name='glossary_url' ),
    url(r'^resources/conventional_transcription_symbols/$', views.conventional_transcription_symbols, name='conventional_transcription_symbols_url'),

    url(r'^stories/$', views.stories, name='stories_url' ),
    url( r'^stories/(?P<story_id>.*)/$', views.individual_story, name='test_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='index_url') ),

    ]
