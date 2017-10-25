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
    url(r'^resources/$', views.resources, name=u'resources_url' ),
    url(r'^resources/bibliography$', views.bibliography, name=u'bibliography_url' ),
    url(r'^resources/timeline$', views.timeline, name=u'timeline_url' ),
    url(r'^resources/guide_to_searching$', views.guide_to_searching, name=u'guide_to_searching_url' ),
    url(r'^resources/glossary$', views.glossary, name=u'glossary_url' ),


    url(r'^stories/$', views.stories, name=u'stories_url' ),
    url( r'^stories/(?P<story_id>.*)/$', views.individual_story, name=u'test_url' ),

    # url(r'^viewinscr/(?P<inscrid>.*)/get_maplet/$', 'iip_search_app.views.get_maplet', name='maplet_url'),

    # url(r'^stories/$', views.stories, name=u'stories_url' ),
    



    # url(r'^stories/theodotos2$', views.theodotos, name=u'theodotos_url2' ),
    # url(r'^stories/theodotos$', views.test, name=u'theodotos_url' ),





    # url(r'^stories/heliodorus$', views.heliodorus, name=u'heliodorus_url' ),
    # url(r'^stories/ossuaries$', views.ossuaries, name=u'ossuaries_url' ),
    
    # url(r'^stories/kokhba$', views.kokhba, name=u'kokhba_url' ),
    # url(r'^stories/synagogue_waypoint$', views.synagogue_waypoint, name=u'synagogue_waypoint_url' ),



    
    # url( r'^$', redirect_to, {'url': 'mapsearch/'} ),

    # url( r'^admin/', include(admin.site.urls) ),

    # url( r'^login/$',  views.login, name=u'login_url' ),

    # url( r'^logout/$',  views.logout, name=u'logout_url' ),

    # url( r'^results/$',  views.results, name=u'results_url' ),

    # url( r'^search/$',  views.results, name=u'search_url' ),

    # url( r'^api/$', views.api_wrapper, name=u"api_wrapper"),

    # url( r'^viewinscr/(?P<inscrid>.*)/$', views.viewinscr, name='inscription_url'),

    # url( r'^view_xml/(?P<inscription_id>.*)/$', views.view_xml, name=u'xml_url' ),

    # url( r'^info/(?P<info_id>.*)/$', views.info, name=u'info_url' ),

    # url( r'^edit_info/$', views.edit_info, name=u'edit_info_url' ),


    # url( r'^temp/$', views.temp, name=u'temp_url' ),


    url( r'^$',  RedirectView.as_view(pattern_name='index_url') ),

    ]
