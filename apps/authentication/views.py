from datetime import datetime
from hashlib import sha512
import logging

import dateutil.parser
import ujson as json

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout, get_user_model
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View

from rest_framework.renderers import JSONRenderer

from authentication.forms import (
    PhoneNumberLoginForm,
    EmailLoginForm,
    SetPasswordForm,
    ResendSetPasswordForm,
)
from authentication.models import Token


logger = logging.getLogger(__name__)


def user_is_admin_type(user):
    logger.warning("Checking user permissions.")
    if user.is_anonymous:
        logger.warning("rejecting anonymous user")
        return False

    if user.is_superuser:
        logger.warning("accepting superuser")
        return True

    groups = ["hotline_admins", "dashboard_admins"]
    for group in groups:
        if user.groups.filter(name=group).count() == 1:
            logger.warning(f"accepting {group}")
            return True
    return False


class AuthErrorView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'auth-error.html')


class LoginView(auth_views.LoginView, View):
    template_name = "login.html"
    redirect_authenticated_user = True
    authentication_form = PhoneNumberLoginForm

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        # authenticate user
        auth_login(self.request, form.get_user())

        # get token and add ip_address hash and user agent
        token, created = Token.objects.get_or_create(user=form.get_user())
        token.cycle(self.request)

        return HttpResponseRedirect(self.get_success_url())


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # delete user auth token
            request.user.auth_token.delete()

            # TODO: consider lifting into an task/action
            if hasattr(request.user,'agent') and request.user.agent:
                request.user.agent.status = 'offline'
                request.user.agent.save()

            # finally, log out
            logout(request)

        context = dict(title="Logged Out")
        return redirect(reverse("authentication:login"))


class LoginRedirectView(View):
    """redirect to /authentication/login"""

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return redirect("authentication:login")


class LogoutRedirectView(View):
    """redirect to /authentication/logout"""

    def get(self, request, *args, **kwargs):
        return redirect("authentication:logout")


class PasswordResetView(auth_views.PasswordResetView):
    # forgot password view
    template_name = "forgot-password.html"
    redirect_authenticated_user = True
    extra_context = dict(title="Forgot Password")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    # forgot password confirmation view
    template_name = "forgot-password-confirmation.html"
    redirect_authenticated_user = True
    extra_context = dict(title="Forgot Password Email Sent")


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    # reset password view
    template_name = "password-reset.html"
    redirect_authenticated_user = True
    extra_context = dict(title="Password Reset")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    # reset password confirm view
    template_name = "password-reset-complete.html"
    extra_context = dict(title="Password Reset Complete")


class SetPasswordView(View):
    def token_is_valid(self, request, token):
        context = dict(title="Bad Token")

        User = get_user_model()
        value = User.load_set_password_token(token)

        if not value:
            context["reason"] = "This token is not valid."
            return False, render(request, "set-password-bad-token.html", context)

        phone_number, expires = value.split("::")

        # make sure the expires value is a valid int
        if not expires.isdigit():
            context["reason"] = "This token is invalid."
            return False, render(request, "set-password-bad-token.html", context)

        # make sure user with phone number exists
        user_queryset = User.objects.filter(phone_number=phone_number)
        if not user_queryset.exists():
            # invalid token
            context["reason"] = "This token is invalid."
            return False, render(request, "set-password-bad-token.html", context)

        # check if the user has a password set
        user = user_queryset.first()
        self.user = user
        if user.password not in [None, ""]:
            context["reason"] = "This token has already been used."
            return False, render(request, "set-password-bad-token.html", context)

        # check if the token is expired
        expiry = datetime.utcfromtimestamp(int(expires)).astimezone()
        if timezone.now() > expiry:
            context["reason"] = "This token has expired."
            return False, render(request, "set-password-bad-token.html", context)

        return True, None

    def get(self, request, token, **kwargs):
        is_valid, response = self.token_is_valid(request, token)
        if not is_valid:
            return response

        # return the set password form
        return render(request, "set-password.html", {"form": SetPasswordForm()})

    def post(self, request, token, **kwargs):
        is_valid, response = self.token_is_valid(request, token)
        if not is_valid:
            return response
        # validate and save form
        form = SetPasswordForm(request.POST)
        if not form.is_valid():
            return render(request, "set-password.html", {"form": form})

        user = form.save(self.user)
        return render(request, "set-password-complete.html", {"form": form})


class ResendSetPasswordView(LoginRequiredMixin, View):
    @method_decorator(user_passes_test(user_is_admin_type, login_url="/access-denied"))
    def dispatch(self, *args, **kwargs):
        return super(ResendSetPasswordView, self).dispatch(*args, **kwargs)

    def get(self, request, **kwargs):
        return render(
            request, "resend-set-password.html", {"form": ResendSetPasswordForm()}
        )

    def post(self, request, **kwargs):
        form = ResendSetPasswordForm(request.POST)
        if not form.is_valid():
            return render(request, "resend-set-password.html", {"form": form})

        user = form.save()
        context = {"form": form, "phone_number": user.phone_number__prettified}
        return render(request, "resend-set-password-complete.html", context)


class EmailVerificationView(View):
    def get(self, request, token, **kwargs):
        context = dict(title="Email Verification", message="")
        return render(request, "email-verification.html", context)
