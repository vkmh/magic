from django.conf.urls import *
from django.shortcuts import *

urlpatterns = patterns(
    '',
    url(r'^$', 'trackingapp.views.home', name="home"),
    url(r'^api/(?P<api_key>[0-9a-z]+)/$', 'trackingapp.views.api', name="api"),


    url(r'^source/(?P<source_id>[0-9]+)/?$', 'trackingapp.views.source_details', name="source"),
    url(r'^expansion/(?P<expansion_id>[0-9]+)/?$', 'trackingapp.views.expansion_details', name="expansion"),
)
