from django.conf.urls import url

from .views import (
    registration_view, AuthLoginView, AuthLogoutView,
    AuthPasswordChangeView,
    AuthPasswordEmailResetView, AuthPasswordResetConfirmView,
    auth_phone_verify_code_view, auth_phone_send_verification_code_view,
    auth_form_successful_view, auth_form_unsuccessful_view,
    auth_activation_confirm_view, find_lost_account_view
)

urlpatterns = [
    # Basic auth operations
    url(r'login$', AuthLoginView.as_view(),
        name='login'),
    url(r'logout$', AuthLogoutView.as_view(),
        name='logout'),

    # Registration
    url(r'register$', registration_view,
        name='register'),

    # Find Password or ID
    url(r'find_lost_account$', find_lost_account_view,
        name='find_lost_account'),

    # Regarding Password management
    url(r'passwordchange$', AuthPasswordChangeView.as_view(),
        name='password_change'),
    url(r'reset_password_email$', AuthPasswordEmailResetView.as_view(),
        name='password_email_reset'),
    url(r'reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        AuthPasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Phone registration
    url(r'verify_phone_code$', auth_phone_verify_code_view,
        name='auth_phone_verify_code'),
    url(r'send_phone_verification_code$', auth_phone_send_verification_code_view,
        name='auth_phone_send_verification_code'),

    # Account activation
    url(r'activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z\-]{14,20})/$',
        auth_activation_confirm_view, name='account_activation_confirm'),

    # Success and Unsuccessful pages
    url(r'(?P<label>[A-Za-z_]+)/successful$', auth_form_successful_view,
        name='form_successful'),
    url(r'(?P<label>[A-Za-z_]+)/unsuccessful$', auth_form_unsuccessful_view,
        name='form_unsuccessful'),
]