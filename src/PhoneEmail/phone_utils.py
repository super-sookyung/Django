import random

# a google powered phonenumber project!
import phonenumbers

# twilio message sending API
from twilio.rest import Client

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from .CONSTANTS import (ALLOWED_COUNTRY_CODE, )

from django.conf import settings


def _phonenumber_obj_to_e164(phone_number):
    return phonenumbers.format_number(
        phone_number,
        phonenumbers.PhoneNumberFormat.E164)


def _validate_phone_number(value):
    value = str(value)
    phone_number = phonenumbers.parse(value, )
    if phonenumbers.is_valid_number(phone_number):
        if str(phone_number.country_code) in ALLOWED_COUNTRY_CODE.keys():
            return phonenumbers.format_number(
                phone_number,
                phonenumbers.PhoneNumberFormat.E164)
        else:
            msg = _("country code not supported yet and this shouldn't "
                    + "have happened anyways. It should have been checked "
                    + "while registering!")
    else:
        msg = _("phone number is not valid!!")
    raise ValueError(msg)


def _random_verification_number(length):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


"""
Implement a singleton design pattern so that, we can ensure that
there is only one class instance sending messages
Therefore we can take care of message limits, etc without the need 
to save things in the database.
Maybe a db level singleton desgin could also be useful
"""


class PhoneMessageSender(object):
    # Do not allow receiving messages! We don't need it

    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(PhoneMessageSender, cls).__new__(
                cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        if settings.PHONE_BACKEND == "Twilio":
            self.sender_module = self._twilio_sender
            self.client = Client()  # add credentials later from settings

        elif settings.PHONE_BACKEND == 'Local':
            self.sender_module = self._local_printer

        else:
            raise AttributeError()

    def send_message(self, body, from_=None, to=None):
        self.sender_module(body=body, from_=from_, to=to)

    def _twilio_sender(self, from_, to, body):
        self.client()
        # add later

    def _local_printer(self, from_, to, body):
        phone_msg = _(
            f"from: Local \n"
            f"to: {to} \n"
            f"body: {body}")
        print(phone_msg)