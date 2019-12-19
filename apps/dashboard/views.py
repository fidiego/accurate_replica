import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from fax.models import Fax
from fax.forms import OutboundFaxForm


class DashboardHomeRedirectView(View):
    """redirect to dashboard home"""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return redirect("authentication:login")


class Home(LoginRequiredMixin, View):
    def get(self, request):
        faxes = Fax.objects.all().order_by('-created_on')
        return render(request, "home.html", context={'faxes': faxes})


class FaxDetail(LoginRequiredMixin, View):
    def get(self, request, uuid):
        fax = Fax.objects.get(uuid=uuid)
        return render(request, "fax-detail.html", context={'fax': fax})


class NewFax(LoginRequiredMixin, View):
    def get(self, request):
        form = OutboundFaxForm()
        return render(request, "new-fax.html", context={'form': form})

    def post(self, request):
        form = OutboundFaxForm(request.POST, request.FILES, created_by=request.user)
        if form.is_valid():
            fax = form.save()
            return redirect('dashboard:fax-detail', uuid=str(fax.uuid))
        else:
            return render(request, 'new-fax.html', context={'form': form})
