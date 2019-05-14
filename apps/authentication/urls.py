from django.conf.urls import url, include

from authentication.views import AuthErrorView

from authentication.views import LoginView
from authentication.views import LogoutView

from authentication.views import EmailVerificationView

from authentication.views import PasswordResetCompleteView
from authentication.views import PasswordResetConfirmView
from authentication.views import PasswordResetDoneView
from authentication.views import PasswordResetView
from authentication.views import ResendSetPasswordView
from authentication.views import SetPasswordView


app_name = "authentication"


urlpatterns = [
    url("auth-error", AuthErrorView.as_view(), name="auth-error"),
    url("login", LoginView.as_view(), name="login"),
    url("logout", LogoutView.as_view(), name="logout"),
    url(
        "resend-set-password",
        ResendSetPasswordView.as_view(),
        name="resend_set_password",
    ),
    url(
        r"set-password/(?P<token>[\w+]{35}:[\w+]{6}:[\w+]{27})",
        SetPasswordView.as_view(),
        name="set_password",
    ),
    url(
        "forgot-password/confirmation",
        PasswordResetCompleteView.as_view(),
        name="password_reset_done",
    ),
    url("forgot-password", PasswordResetView.as_view(), name="forgot-password"),
    url(
        "password-reset-complete",
        PasswordResetDoneView.as_view(),
        name="password_reset_complete",
    ),
    url(
        r"password-reset/(?P<uidb64>[\w+]+):(?P<token>[\w+]+)",
        PasswordResetView.as_view(),
        name="password_reset_confirm",
    ),
    url(
        "verify/email/<str:token>",
        EmailVerificationView.as_view(),
        name="email-verification",
    ),
]
