# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView, TemplateView
from iip_smr_web_app import views


admin.autodiscover()

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url( r'^login/$',  views.login, name=u'login_url' ),
    url( r'^logout/$',  views.logout, name=u'logout_url' ),
    url( r'^old_search/$',  views.old_results, name=u'oldsearch_url' ),
    url( r'^api/$', views.api_wrapper, name=u"api_wrapper"),
    url( r'^viewinscr/(?P<inscrid>.*)/$', views.viewinscr, name='inscription_url'),
    url( r'^view_xml/(?P<inscription_id>.*)/$', views.view_xml, name=u'xml_url' ),
    url( r'^info/(?P<info_id>.*)/$', views.info, name=u'info_url' ),
    url( r'^edit_info/$', views.edit_info, name=u'edit_info_url' ),
    url( r'^results/$',  views.results, name=u'results_url' ),

    ##NEW
    url(r'^about/$', views.why_inscription,  name=u'about_url' ),
    url(r'^about/why_inscription$', views.why_inscription,  name=u'why_inscription_url' ),
    url(r'^about/project_description$', views.project_description,  name=u'project_description_url' ),
    url(r'^about/documentation$', views.documentation,  name=u'documentation_url' ),
    url(r'^about/api$', views.api,  name=u'api_url' ),
    url(r'^about/funding$', views.funding,  name=u'funding_url' ),
    url(r'^about/team$', views.team,  name=u'team_url' ),
    url(r'^about/copyright$', views.copyright,  name=u'copyright_url' ),
    url(r'^index/$', views.index, name=u'index_url' ),
    url(r'^contact/$', views.contact, name=u'contact_url' ),
    url(r'^mapsearch/$', views.results, name=u'mapsearch_url' ),
    url(r'^mapsearch/load_layers/$', views.load_layers, name='load_layers'),
    url(r'^resources/$', views.bibliography, name=u'resources_url' ),
    url(r'^resources/bibliography$', views.bibliography, name=u'bibliography_url' ),
    url(r'^resources/timeline$', views.timeline, name=u'timeline_url' ),
    url(r'^resources/guide_to_searching$', views.guide_to_searching, name=u'guide_to_searching_url' ),
    url(r'^resources/glossary$', views.glossary, name=u'glossary_url' ),
    url(r'^resources/conventional_transciption_symbols$', views.conventional_transciption_symbols, name=u'conventional_transciption_symbols_url'),
    url(r'^stories/$', views.stories, name=u'stories_url' ),
    url( r'^stories/(?P<story_id>.*)/$', views.individual_story, name=u'test_url' ),

    url( r'^$',  RedirectView.as_view(pattern_name='index_url') ),

    ]
