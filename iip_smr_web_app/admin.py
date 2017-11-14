# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from .models import StaticPage, StoryPage
from django.contrib import admin
from .forms_admin import AdminStaticPageForm, AdminStoryPageForm

class StaticPageAdmin(admin.ModelAdmin):
    list_display = [ 'title' ]
    form = AdminStaticPageForm
    ordering = [ 'title' ]
    prepopulated_fields = {"slug": ("title",)}


class StoryPageAdmin(admin.ModelAdmin):
	list_display = ['title']
	form = AdminStoryPageForm





admin.site.register( StaticPage, StaticPageAdmin )
admin.site.register( StoryPage, StoryPageAdmin )


