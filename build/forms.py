# Stdlib imports

# Core Django imports
from django import forms
from django.contrib.auth.models import User
from .chocolate import replace_all

from lxml import etree
import urllib2, urllib
import datetime

# Third-party app imports

# Imports from apps
from .models import *

#    FORMS
# Create forms here.
class AliasForm(forms.ModelForm):

    class Meta:
        model = Alias
        exclude = ('bundle',)


class BundleForm(forms.ModelForm):
    name = forms.CharField( initial='Enter name here', required=True, max_length=50) 

    class Meta:
        model = Bundle              
        fields = ('name', 'bundle_type',)

    def clean(self):
        cleaned_data = self.cleaned_data
        name = cleaned_data.get('name')
        if len(name) <= 255:
            name_edit = name
            name_edit = name_edit.lower()
            name_edit = replace_all(name_edit, ' ', '_') # replace spaces with underscores
            if name_edit.endswith("bundle"):
                name_edit = name_edit[:-7] # seven because there is probably an underscore by now
            if name_edit.find(':') != -1:
                raise forms.ValidationError("The colon (:) is used to delimit segments of a urn and thus is not permitted within a bundle name.")
        else:
            raise forms.ValidationError("The length of your bundle name is too large");


class CitationInformationForm(forms.ModelForm):

    description = forms.CharField(required=True)
    publication_year = forms.CharField(required=True)

    class Meta:
        model = Citation_Information
        exclude = ('bundle',)


class CollectionsForm(forms.ModelForm):
    has_document = forms.BooleanField(required=True, initial=True)
    has_context = forms.BooleanField(required=True, initial=True)
    has_xml_schema = forms.BooleanField(required=True, initial=True)

    class Meta:
        model = Collections
        exclude = ('bundle',)

class ProductDocumentForm(forms.ModelForm):
    acknowledgement_text = forms.CharField(required=False)
    author_list = forms.CharField(required=False)
    copyright = forms.CharField(required=False)
    description = forms.CharField(required=False)
    document_editions = forms.CharField(required=False)
    document_name = forms.CharField(required=False)
    doi = forms.CharField(required=False)
    editor_list = forms.CharField(required=False)
    publication_date = forms.CharField(required=True)
    revision_id = forms.CharField(required=False)

    class Meta:
        model = Product_Document
        exclude = ('bundle',)

class ProductBundleForm(forms.ModelForm):

    class Meta:
        model = Product_Bundle
        exclude = ('bundle',)

class ProductCollectionForm(forms.ModelForm):

    class Meta:
        model = Product_Collection
        exclude = ('bundle', 'collection')



