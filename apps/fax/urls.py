from django.urls import path

from fax.views import FaxStatusCallback, FaxSentView, FaxReceivedView


app_name = "fax"


urlpatterns = [
    path("status/<uuid:uuid>/", FaxStatusCallback.as_view(), name="status-callback"),
    path("sent", FaxSentView.as_view(), name="sent"),
    path("received", FaxReceivedView.as_view(), name="received"),
]
