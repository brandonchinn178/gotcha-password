from django.conf.urls import url

from base.views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^create-account/$', CreateAccountView.as_view(), name='create-account'),
    url(r'^create-account/setup/$', SetupImagesView.as_view(), name='setup-images'),
    url(r'^create-account/success/$', CreateSuccessView.as_view(), name='create-success'),
]
