from django import forms
from pagedown.widgets import AdminPagedownWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from .models import StaticPage
from .widgets import AddAnotherWidgetWrapper



class AdminStaticPageForm(forms.ModelForm):
    content = forms.CharField( widget=AdminPagedownWidget() )

    class Meta:
        model = StaticPage
        fields = ( 'slug', 'title_header', 'title', 'content' )
