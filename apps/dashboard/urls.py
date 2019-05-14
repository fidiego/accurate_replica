from django.urls import path
from django.conf.urls import url

from dashboard.views import Home, FaxDetail


app_name = "dashboard"


urlpatterns = [
    path(r'fax/<uuid:uuid>', FaxDetail.as_view(), name="fax-detail"),
    path(r'^$', Home.as_view(), name="home"),
    url(r'^(?:.*)/?$', Home.as_view(), name="home"),
]
