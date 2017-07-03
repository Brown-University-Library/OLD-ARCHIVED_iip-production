# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .models import StaticPage
from django.contrib import admin
from .forms_admin import AdminStaticPageForm

class StaticPageAdmin(admin.ModelAdmin):
    list_display = [ 'title' ]
    form = AdminStaticPageForm
    ordering = [ 'title' ]
    prepopulated_fields = {"slug": ("title",)}



admin.site.register( StaticPage, StaticPageAdmin )
