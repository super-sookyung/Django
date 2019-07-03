from datetime import timedelta
# for time check

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
# for models

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.http import base36_to_int, int_to_base36
# for crypto

from PhoneEmail.fields import PhoneNumberField
from PhoneEmail.phone_utils import _random_verification_number
from PhoneEmail.email_utils import _random_verification_string
# phone number related

from django.conf import settings

User = settings.AUTH_USER_MODEL


class EmailVerificationCode(models.Model):
    email = models.EmailField(null=False, blank=False,
                              db_index=True, max_length=150)

    verification_code = models.CharField(max_length=30)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = (('email', 'verification_code'), )
        ordering = ('created', )

    def __str__(self):
        return f"{self.email}: {self.verification_code}: {self.created}"

    def clean(self):
        if self.email == "null":
            msg = _("Email should not be null")
            raise ValidationError(msg)

    @staticmethod
    def _generate_email_verification_number(length1=5, length2=12):
        ver_string = ''.join([
            _random_verification_string(length1),
            '-',
            _random_verification_string(length2)])
        return ver_string

    @property
    def is_not_expired(self):
        if self.email:
            valid = (self.created - timezone.now()) \
                < timedelta(days=settings.USER_ACTIVATION_EMAIL_VALIDITY_TIME[1])
            return valid

    def verification_code_matches(self, verification_code):
        return self.verification_code == verification_code


class PhoneVerificationCode(models.Model):
    user_phone = PhoneNumberField(
        null=False, blank=True, db_index=True, max_length=16)

    verification_code = models.CharField(max_length=30)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        unique_together = (('user_phone', 'verification_code'), )
        ordering = ('created', )

    def __str__(self):
        return f"{self.user_phone}: {self.verification_code}: {self.created}"

    def clean(self):
        if self.user_phone == "null":
            msg = _("Phone number should not be null")
            raise ValidationError(msg)

    @staticmethod
    def _generate_phone_verification_number(length=5):
        return _random_verification_number(length)

    @property
    def is_not_expired(self):
        if self.user_phone:
            valid = (self.created - timezone.now()) \
                < timedelta(minutes=settings.PASSWORD_RESET_PHONE_VALIDITY_TIME[1])
            return valid

    def verification_code_matches(self, verification_code):
        return self.verification_code == verification_code