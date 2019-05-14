from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from fax.models import Fax


class DashboardHomeRedirectView(View):
    """redirect to dashboard home"""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return redirect("authentication:login")


class Home(View):
    def get(self, request):
        faxes = Fax.objects.all().order_by('-created_on')
        return render(request, "home.html", context={'faxes': faxes})


class FaxDetail(View):
    def get(self, request, uuid):
        fax = Fax.objects.get(uuid=uuid)
        return render(request, "fax-detail.html", context={'fax': fax})
