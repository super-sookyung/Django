import phonenumbers

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import (
    AuthenticationForm, UsernameField, UserCreationForm,
)
from django.core.exceptions import ValidationError

from django.contrib.auth import (
    get_user_model, authenticate, password_validation
)

from PhoneEmail.fields import FormPhoneField
from PhoneEmail.validators import non_phone_number_element_regex_finder
from PhoneEmail.phone_utils import _phonenumber_obj_to_e164

User = get_user_model()


class AuthPhoneOnlyVerificationForm(forms.Form):
    user_phone = FormPhoneField(max_length=20)

    def __init__(self, *args, **kwargs):
        super(AuthPhoneOnlyVerificationForm, self).__init__(*args, **kwargs)
        self.fields['user_phone'].label = "Phone Number"

    def clean_user_phone(self):
        user_phone = self.cleaned_data['user_phone']
        user_phone = user_phone.replace("-", "")
        msg = "Phone number not valid"
        if not non_phone_number_element_regex_finder.match(user_phone):
            raise ValidationError(_(msg))
        user_phone = str(user_phone)
        phone_number = phonenumbers.parse(user_phone, )
        if not phonenumbers.is_valid_number(phone_number):
            raise ValidationError(_(msg))
        return _phonenumber_obj_to_e164(phone_number)


class AuthPhoneVerificationForm(AuthPhoneOnlyVerificationForm):
    # directly inherit the phone only form!
    verification_code = forms.CharField(max_length=50)

    def __init__(self, *args, **kwargs):
        super(AuthPhoneVerificationForm, self).__init__(*args, **kwargs)
        self.fields['verification_code'].label = "Verification Number"


class UserAuthenticationForm(AuthenticationForm):
    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )

    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "password")

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.
        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.
        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class UserRegistrationForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'email_not_unique': _("The Email is not Availible!")
    }

    email = forms.EmailField(label=_("Email")
                             )

    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
                                widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def clean_email(self):
        cleaned_email = self.cleaned_data.get('email')
        email_exists = User.objects.filter(email=cleaned_email
                                           ).exists()
        if email_exists:
            raise forms.ValidationError(
                self.error_messages['email_not_unique'],
                code='email_not_unique',
            )
        return cleaned_email