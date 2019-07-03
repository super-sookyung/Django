from io import BytesIO
	
from PIL import Image
import phonenumbers

from django.db import models
from django import forms
from django.core.files.images import ImageFile
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from .phone_utils import _validate_phone_number, _phonenumber_obj_to_e164

"""
Custom Field creation for phone_number and email fields
"""


class FormPhoneField(forms.CharField):

    def __init__(self, *args, **kwargs):
        super(FormPhoneField, self).__init__(*args, **kwargs)

    def validate(self, value):
        """Check if value consists only of valid phone."""
        # Use the parent's handling of required fields, etc.
        _validate_phone_number(value)

    def clean(self, value):
        try:
            phone_number = phonenumbers.parse(value)
            return _phonenumber_obj_to_e164(phone_number)
        except:
            raise forms.ValidationError("Invalid Phone Number")


class PhoneNumberField(models.CharField):

    def __init__(self, *args, **kwargs):
        super(PhoneNumberField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(PhoneNumberField, self).deconstruct()
        return name, path, args, kwargs

    def to_python(self, value):
        if self.null and value in self.empty_values:
            return None
        """
        check if phone number is valid by the broadest filter
        note that it will be a ongoing string without any separators
        to classify country code!
        Since SMS API requires a phone number without separator values.
        If there is a need to create area code, do it on the front end,
        or when serializing!
        """
        return value

    def get_prep_value(self, value):
        if not value:
            return "null"
        if value == "null":
            return "null"
        if isinstance(value, phonenumbers.phonenumber.PhoneNumber):
            # serializer should be passing Phonenumber object!
            return _phonenumber_obj_to_e164(value)
        return _validate_phone_number(value)