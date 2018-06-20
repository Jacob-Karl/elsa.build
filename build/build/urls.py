# Stdlib imports

# Core Django imports
from django.conf.urls import url, include

# Third-party app imports

# Imports from apps
from . import views



app_name='build'
urlpatterns = [
    # Alias
    url(r'^(?P<pk_bundle>\d+)/alias/$', views.alias, name='alias'),

    # Build
    url(r'^$', views.build, name='build'),

    # Bundle
    url(r'^(?P<pk_bundle>\d+)/$', views.bundle, name='bundle'), # Secure
    url(r'^(?P<pk_bundle>\d+)/confirm_delete/$', views.bundle_delete, name='bundle_delete'), # Secure
    url(r'^(?P<pk_bundle>\d+)/download/$', views.bundle_download, name='bundle_download'), # Need to secure.

    # Citation_Information
    url(r'^(?P<pk_bundle>\d+)/citation_information/$', views.citation_information, name='citation_information'),

    # Collections




    # Document
    url(r'^(?P<pk_bundle>\d+)/document/$', views.document, name='document'),


    # Context

    # XML_Schema

    # Data

    # Product_Bundle


    # Product Bundle



    # Product Collection



    # TEST
]
