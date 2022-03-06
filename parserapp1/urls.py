from django.conf.urls import url
from django.urls import path,re_path


import parserapp1.views as parserapp1

app_name = 'parserapp1'

urlpatterns = [
   re_path(r'^$', parserapp1.index, name='index'),
   path('startThread', parserapp1.startParseTask, name='startParseTask'), #1st button
   path('startParseDb', parserapp1.startParseDb, name='startParseDb'), #and so on
   url(r'^updateDb/(?P<id>[0-9]+)/?$', parserapp1.updateDb, name='updateDb'),
   url(r'^updateDbAll/$', parserapp1.updateDbAll, name='updateDbAll'),
   url(r'^checkThread/(?P<id>[0-9]+)/?$', parserapp1.checkParseTask, name='checkParseTask'), #checkcurrent state
]