"""accurate_replica URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.urls import urlpatterns as auth_urlpatterns
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic.base import RedirectView

from dashboard.views import DashboardHomeRedirectView

from authentication.views import LogoutRedirectView, LoginRedirectView


urlpatterns = [
    # admin site
    path(f"{settings.ADMIN_SITE_URL}/", admin.site.urls),
    # fax handler views
    path("twilio/fax/", include("fax.urls", namespace="fax")),
    # authentication views
    path("authentication/", include("authentication.urls", namespace="authentication")),
    url("login$", LoginRedirectView.as_view(), name="login"),
    url("logout$", LogoutRedirectView.as_view(), name="logout"),
    # social auth and such
    url(r"^", include("social_django.urls", namespace="social")),
    url(r"^", include((auth_urlpatterns, "auth"))),
    # dashboard views
    url("dashboard", include("dashboard.urls", namespace="dashboard")),
    # favicon
    url(
        r"^favicon.ico$",
        RedirectView.as_view(url=staticfiles_storage.url("img/favicon.ico")),
        name="favicon",
    ),
    # fallback & redirect
    url("", DashboardHomeRedirectView.as_view(), name="fallback"),
]
