# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from django.views.generic import RedirectView
from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
  # /
  path('', views.home, name='home'),
  # TEMPORARY
  path('signin', views.sign_in, name='signin'),
  path('signout', views.sign_out, name='signout'),
  path('callback', views.callback, name='callback'),
  path('calendar', views.calendar, name='calendar'),
  path('calendar/download', views.calendar_download, name='calendarDownload'),
  path('presence', views.presence, name='presence'),
  path('autotag', views.autotag, name='autotag'),
  url(r'^favicon\.ico$',RedirectView.as_view(url='/static/tamtt/images/favicon.ico')),
]
