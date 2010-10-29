from django.conf.urls.defaults import *
from django.http import HttpResponsePermanentRedirect
from django.views.generic.simple import direct_to_template

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^crossfit/', include('crossfit.workout_tracker.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

	url(r'^password_reset/$',     'django.contrib.auth.views.password_reset',name='password_reset'),
    (r'^password_reset/done/$','django.contrib.auth.views.password_reset_done'),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm'),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    (r'^accounts/login/$',lambda request: HttpResponsePermanentRedirect('/crossfit')),
    
    (r'^robots.txt$', direct_to_template, {'template':'robots.txt', 'mimetype':'text/plain'}),
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': 'http://192.168.1.100/~nathan/crossfit/images/favicon.ico'})
)
