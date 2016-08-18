from app import views

from django.conf import settings
from django.conf.urls import patterns
from django.conf.urls import url
from django.views.static import serve as django_static_serve

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       # url(r'^admin/', include(admin.site.urls)),
                       url(r'^/?$', views.home),
                       url(r'^static/(?P<path>.*)$', django_static_serve, {'document_root': settings.STATIC_ROOT}))
