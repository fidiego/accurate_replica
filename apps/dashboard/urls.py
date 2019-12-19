from django.urls import path
from django.conf.urls import url

from dashboard.views import Home, FaxDetail, NewFax


app_name = "dashboard"


urlpatterns = [
    url("fax/new", NewFax.as_view(), name="new-fax"),
    path("fax/<uuid:uuid>", FaxDetail.as_view(), name="fax-detail"),
    path("", Home.as_view(), name="home"),
]
