# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'iip.views.home', name='home'),
    # url(r'^iip/', include('iip.foo.urls')),

    # url( r'^hello/', u'iip_search_app.views.hello', name=u'search_hello' ),
    # url( r'^search/', u'iip_search_app.views.iip_results', name=u'search_iip_results' ),

    url( r'^', include('iip_search_app.urls_app') ),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
