import logging

from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import AuthenticationForm
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _

from core.formatters import e164_format_phone_number, InvalidUSPhoneNumberException


logger = logging.getLogger(__name__)


class PhoneNumberLoginForm(AuthenticationForm):
    username = forms.CharField(label=_("Phone Number"), max_length=17)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())
    password.widget.attrs.update(
        {
            "class": "pa2 input-reset ba w-100 bg-near-white b--near-black near-black",
            "placeholder": "*******",
        }
    )

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(PhoneNumberLoginForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field("phone_number")
        if self.fields["username"].label is None:
            self.fields["username"].label = capfirst(self.username_field.verbose_name)

    def clean_username(self):
        value = self.cleaned_data["username"].strip()
        try:
            formatted = e164_format_phone_number(value)
            return formatted
        except InvalidUSPhoneNumberException as e:
            logger.exception(e)
        raise forms.ValidationError("Expecting a 10-digit us phone number.")

    def clean_password(self):
        return self.cleaned_data["password"].strip()


class EmailLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())
    password.widget.attrs.update(
        {
            "class": "pa2 input-reset ba w-100 bg-near-white b--near-black near-black",
            "placeholder": "*******",
        }
    )

    def clean_username(self):
        return self.cleaned_data["username"].strip().lower()

    def clean_password(self):
        return self.cleaned_data["password"].strip()


class SetPasswordForm(forms.Form):
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput())
    password2 = forms.CharField(
        label=_("Confirm Password"), widget=forms.PasswordInput()
    )
    password.widget.attrs.update(
        {
            "class": "pa2 input-reset ba w-100 bg-near-white b--near-black near-black",
            "placeholder": "*******",
            "autofocus": True,
        }
    )
    password2.widget.attrs.update(
        {
            "class": "pa2 input-reset ba w-100 bg-near-white b--near-black near-black",
            "placeholder": "*******",
        }
    )

    def clean_password(self):
        return self.cleaned_data["password"].strip()

    def clean_password2(self):
        return self.cleaned_data["password2"].strip()

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password", "")
        password2 = cleaned_data.get("password2", "")

        if len(password2) < 12:
            raise forms.ValidationError("Password must be at least 12 characters long.")

        if password != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, user):
        password2 = self.cleaned_data.get("password2")
        user.set_password(password2)
        user.verify_phone_number()
        user.save()
        return user


class ResendSetPasswordForm(forms.Form):
    phone_number = forms.CharField(label=_("Phone Number"), max_length=16)

    def clean_phone_number(self):
        value = self.cleaned_data["phone_number"].strip()
        numbers = "".join([c for c in value if c.isdigit()])
        if value[0] == "+" and len(numbers) == 11:
            logging.warning("E.164 format received")
            username = f"+{numbers}"
            return username
        elif len(numbers) == 10:
            logging.warning("composing E.164 format")
            username = f"+1{numbers}"
            return username

        raise forms.ValidationError("Expecting a 10-digit us phone number.")

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get("phone_number", "")
        user_queryset = get_user_model().objects.filter(phone_number=phone_number)
        if not user_queryset.exists():
            raise forms.ValidationError("Could not find a user with this phone number.")

        user = user_queryset.first()
        if user.password not in [None, ""]:
            raise forms.ValidationError("This user has already set a password.")

        # TODO: this is only for operators at the moment. we'll need to write more cases for other user types
        if not hasattr(user, "operator") or user.operator.deleted_on:
            raise forms.ValidationError("This user is not an operator.")

        return cleaned_data

    def save(self):
        phone_number = self.cleaned_data.get("phone_number")
        user = get_user_model().objects.get(phone_number=phone_number)
        user.operator.send_set_password_prompt()
        return user


class CustomUserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    error_messages = {"password_mismatch": _("The two password fields didn't match.")}
    phone_number = forms.CharField(
        label=_("Phone Number"),
        max_length=16,
        help_text=_("Enter a valid 10-digit US mobile phone number."),
    )
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
    )

    class Meta:
        model = get_user_model()
        fields = ("email", "phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs.update(
                {"autofocus": True}
            )

    def clean_phone_number(self):
        value = self.cleaned_data["phone_number"].strip()
        numbers = "".join([c for c in value if c.isdigit()])
        if value[0] == "+" and len(numbers) == 11:
            return f"+{numbers}"
        elif len(numbers) == 10:
            return f"+1{numbers}"

        raise forms.ValidationError("Expecting a 10-digit us phone number.")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages["password_mismatch"], code="password_mismatch"
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                password_validation.validate_password(password, self.instance)
            except forms.ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
