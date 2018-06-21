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
        exclude = ('',)

class MissionForm(forms.ModelForm):
    class Meta:
        model = Mission
        exclude = ('',)

class InstrumentHostForm(forms.ModelForm):
    class Meta:
        model = InstrumentHost
        exclude = ('',)

class InstrumentForm(forms.ModelForm):
    class Meta:
        model = Instrument
        exclude = ('',)

class TargetForm(forms.ModelForm):
    class Meta:
        model = Target
        exclude = ('',)


class Facility(forms.ModelForm):
    class Meta:
        model = Facility
        exclude = ('',)

"""
12.1  Document

Root Class:Tagged_NonDigital_Object
Role:Concrete

Class Description:The Document class describes a document.

Steward:pds
Namespace Id:pds
Version Id:2.0.0.0
  	Entity 	Card 	Value/Class 	Ind

Hierarchy	Tagged_NonDigital_Object	 	 	 
        	. TNDO_Supplemental	 	 	 
 	        . . Document	 	 	 

Subclass	none	 	 	 

Attribute
	acknowledgement_text	0..1	 	 
 	author_list     	0..1	 	 
 	copyright       	0..1	 	 
 	description	        0..1	 	 
 	document_editions	0..1	 	 
 	document_name	        0..1  An exec decision has been made to make document_name required
 	doi	                0..1	 	 
 	editor_list	        0..1	 	 
 	publication_date	1	 	 
 	revision_id	        0..1	 	 

Inherited Attribute	none	 	 	 
Association	        data_object	        1	Digital_Object	 
 	                has_document_edition	1..*	Document_Edition	 
Inherited Association	none	 	 	 
Referenced from	Product_Document	 	 	 
"""
class ProductDocumentForm(forms.ModelForm):
    document_name = forms.CharField(required=True)
    publication_date = forms.CharField(required=True)
    acknowledgement_text = forms.CharField(required=False)
    author_list = forms.CharField(required=False)
    copyright = forms.CharField(required=False)
    description = forms.CharField(required=False)
    document_editions = forms.CharField(required=False)
    doi = forms.CharField(required=False)
    editor_list = forms.CharField(required=False)
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



