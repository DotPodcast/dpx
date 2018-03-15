from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from djoser import urls as djoser_urls
from djoser.urls import authtoken as djoser_authtoken
from . import views

router = routers.DefaultRouter()

urlpatterns = [
    url(r'^api/auth/', include(djoser_urls)),
    url(r'^api/auth/', include(djoser_authtoken)),
    url(r'^api/', include(router.urls)),
    url(r'^admin/', admin.site.urls),
]
