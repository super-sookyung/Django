from django.conf.urls import url

from .views import (
    check_email_exists_api_view, check_phone_exists_api_view,
    auth_phone_send_verification_code_api_view, phone_verify_api_view,
    email_password_reset_api_view
)

urlpatterns = [
    # Check Email and Phone
    url(r'email_exists/$', check_email_exists_api_view,
        name='email_exists_check_api'),
    url(r'phone_exists/$', check_phone_exists_api_view,
        name='phone_exists_check_api'),

    # Phone Verification
    url(r'send_phone_verification_code/$', auth_phone_send_verification_code_api_view,
        name='send_phone_verification_code_api'),
    url(r'verify_phone_code/$', phone_verify_api_view,
        name='phone_verify_api'),

    # Email Password Reset
    url(r'password_email_reset/$', email_password_reset_api_view,
        name='email_password_reset_api'),
]