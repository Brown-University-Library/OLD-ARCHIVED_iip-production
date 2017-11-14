from django import forms
from pagedown.widgets import AdminPagedownWidget, PagedownWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from .models import StaticPage, StoryPage
from .widgets import AddAnotherWidgetWrapper



class AdminStaticPageForm(forms.ModelForm):
    content = forms.CharField( widget=AdminPagedownWidget() )

    class Meta:
        model = StaticPage
        fields = ( 'slug', 'title_header', 'title', 'content' )


# class AdminStoryPageForm(forms.ModelForm):
# 	content = forms.CharField( widget=AdminPagedownWidget() )

# 	class Meta:
# 		model = StoryPage
# 		fields = ( 'slug', 'title', 'author',
#         	'date', 'short_summary', 'thumbnail_intro' ,'image', 'content', 'relevant_inscription_id' )

class AdminStoryPageForm(forms.ModelForm):
	content = forms.CharField( widget=AdminPagedownWidget() )

	class Meta:
		model = StoryPage
		fields = ( 'slug', 'title', 'author',
        	'date', 'short_summary', 'thumbnail_intro' ,'thumbnail_image_url', 'content', 'relevant_inscription_id' )