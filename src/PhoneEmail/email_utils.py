import string
import random

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _

from django.contrib.auth import (
    get_user_model
)

User = get_user_model()

chars = string.ascii_letters + string.digits


def _random_verification_string(length):
    return ''.join([random.choice(chars) for _ in range(length)])


def send_activation_email(domain_override=None, to_email=None,
                          subject_template_name=None,
                          email_template_name=None,
                          use_https=False, token=None,
                          from_email=None, request=None, html_email_template_name=None,
                          extra_email_context=None):

    user_instance = User.objects.get(email__iexact=to_email)

    if not domain_override:
        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain
    else:
        site_name = domain = domain_override

    context = {
        'email': to_email,
        'domain': domain,
        'site_name': site_name,
        'uid': urlsafe_base64_encode(force_bytes(user_instance.pk)),
        'user': user_instance,
        'token': token,
        'protocol': 'https' if use_https else 'http',
        **(extra_email_context or {})
    }

    subject = loader.render_to_string(
        subject_template_name, context)
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(
        email_template_name, context)

    email_message = EmailMultiAlternatives(
        subject, body, from_email, [to_email])

    if html_email_template_name is not None:
        html_email = loader.render_to_string(
            html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()