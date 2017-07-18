# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import RedirectView
from iip_smr_web_app import views


admin.autodiscover()

urlpatterns = [

    url( r'^admin/', include(admin.site.urls) ),

    url( r'^login/$',  views.login, name=u'login_url' ),

    url( r'^logout/$',  views.logout, name=u'logout_url' ),

    url( r'^results/$',  views.results, name=u'results_url' ),

    url( r'^search/$',  views.results, name=u'search_url' ),

    url( r'^api/$', views.api_wrapper, name=u"api_wrapper"),

    url( r'^viewinscr/(?P<inscrid>.*)/$', views.viewinscr, name='inscription_url'),

    url( r'^view_xml/(?P<inscription_id>.*)/$', views.view_xml, name=u'xml_url' ),

    url( r'^info/(?P<info_id>.*)/$', views.info, name=u'info_url' ),

    url( r'^edit_info/$', views.edit_info, name=u'edit_info_url' ),


    url( r'^temp/$', views.temp, name=u'temp_url' ),


    url( r'^$',  RedirectView.as_view(pattern_name='search_url') ),

    ]
