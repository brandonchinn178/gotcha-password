from django.conf.urls import url

from base.views import *

urlpatterns = [
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^create-account/$', CreateAccountView.as_view(), name='create-account'),
    url(r'^create-account/images/$', CreateImagesView.as_view(), name='create-images'),
    url(r'^create-account/success/$', CreateSuccessView.as_view(), name='create-success'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^login/verify/$', LoginVerifyView.as_view(), name='login-verify'),
    url(r'^login/success/$', LoginSuccessView.as_view(), name='login-success'),
]
