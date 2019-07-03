from django.http import JsonResponse

# django basic tools
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

# for auth
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site

# for cryptosigning
from datetime import timedelta

from django.contrib.auth.forms import (
    AuthenticationForm, UsernameField, UserCreationForm,
    PasswordResetForm,
)

from PhoneEmail.email_utils import send_activation_email
from PhoneEmail.phone_utils import PhoneMessageSender

from .models import PhoneVerificationCode, EmailVerificationCode
from .forms import (
    UserRegistrationForm, AuthPhoneVerificationForm,
    AuthPhoneOnlyVerificationForm
)

from django.contrib.auth import (
    get_user_model, logout as auth_logout,
)

User = get_user_model()


# phoneverification model
phone_message_sender = PhoneMessageSender()

################################################
################################################
#           Basic Auth : Login Logout
################################################
################################################


class AuthLoginView(auth_views.LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True


class AuthLogoutView(auth_views.LogoutView):
    template_name = "auth/logout.html"


################################################
################################################
#              Registration
################################################
################################################


@sensitive_post_parameters()
def registration_view(request):
    if request.user.is_authenticated():
        return HttpResponse("must logout before registering!",
                            status=403)
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password2']

            registered_user = User.objects.create_user(email=email,
                                                       password=password,
                                                       user_type=10,
                                                       )

            verification_code = EmailVerificationCode()._generate_email_verification_number()
            user_email = registered_user.email

            EmailVerificationCode.objects.create(
                email=user_email, verification_code=verification_code)

            opts = {
                'to_email': user_email,
                'use_https': request.is_secure(),
                'token': verification_code,
                'from_email': 'sogangdjango@noreply.com',
                'email_template_name': 'auth/email/email_content_account_activate.html',
                'subject_template_name': 'auth/email/account_activate_subject.txt',
                'request': request,
                'html_email_template_name': 'auth/email/email_content_account_activate.html',
                'extra_email_context': None
            }

            send_activation_email(**opts)
            return redirect(
                reverse_lazy('auth:form_successful', kwargs={
                             'label': 'user_register'})
            )
        return render(request, 'auth/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
        return render(request, 'auth/register.html', {'form': form})


################################################
################################################
#              Find Lost Account
################################################
################################################


def find_lost_account_view(request):
    auth_logout(request)
    if request.method == "GET":
        password_reset_form = PasswordResetForm()
        phone_verification_send_form = AuthPhoneOnlyVerificationForm()
        phone_verification_form = AuthPhoneVerificationForm()
        context = dict(
            password_reset_form=password_reset_form,
            phone_verification_send_form=phone_verification_send_form,
            phone_verification_form=phone_verification_form)
        return render(request, 'auth/find_lost_account.html', context)


################################################
################################################
#              Password Related
################################################
################################################


class AuthPasswordChangeView(auth_views.PasswordChangeView):
    template_name = "auth/changepassword.html"
    success_url = reverse_lazy('auth:form_successful', kwargs={
                               'label': 'password_change_complete'})


class AuthPasswordEmailResetView(auth_views.PasswordResetView):
    template_name = 'auth/password_reset_email.html'
    email_template_name = 'auth/email/email_content_password_reset.html'
    subject_template_name = 'auth/email/password_reset_subject.txt'
    success_url = reverse_lazy('auth:form_successful', kwargs={
                               'label': 'password_reset_email_sent'})


class AuthPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    token_generator = default_token_generator
    success_url = reverse_lazy('auth:form_successful', kwargs={
                               'label': 'password_change_complete'})


################################################
################################################
#     Phone Registration Raw CODE
################################################
################################################


@sensitive_post_parameters()
def auth_phone_verify_code_view(request):
    if request.method == "POST":
        auth_phone_verification_form = AuthPhoneVerificationForm(request.POST)
        if auth_phone_verification_form.is_valid():
            user_phone = \
                auth_phone_verification_form.cleaned_data['user_phone']

            verification_code = \
                auth_phone_verification_form.cleaned_data['verification_code']

            latest_of_user_reset_data = \
                PhoneVerificationCode.objects.filter(
                    user_phone=user_phone).latest('created')

            if latest_of_user_reset_data:
                if not latest_of_user_reset_data.is_not_expired:
                    auth_phone_verification_form.add_error(
                        None, "Your key has expired")
                    return render(request,
                                  'auth/verify_phone_code.html',
                                  {'auth_phone_verification_form': auth_phone_verification_form}
                                  )
                if not latest_of_user_reset_data.verification_code_matches(verification_code):
                    auth_phone_verification_form.add_error(None, "Wrong Key!")
                    return render(request,
                                  'auth/verify_phone_code.html',
                                  {'auth_phone_verification_form': auth_phone_verification_form}
                                  )
                user_object = get_object_or_404(
                    User, user_phone=user_phone, is_active=True)
                # user.has_usable() add for later!
                return HttpResponse("<h1>verification complete!</h1>")

        else:
            return render(request,
                          'auth/verify_phone_code.html',
                          {'auth_phone_verification_form': auth_phone_verification_form}
                          )
    if request.method == "GET":
        auth_phone_verification_form = AuthPhoneVerificationForm()
        context = dict(
            auth_phone_verification_form=auth_phone_verification_form)
        return render(request, 'auth/verify_phone_code.html', context)


@sensitive_post_parameters()
def auth_phone_send_verification_code_view(request):
    if request.method == "POST":
        auth_phone_only_form = AuthPhoneOnlyVerificationForm(request.POST)
        if auth_phone_only_form.is_valid():
            user_phone = auth_phone_only_form.cleaned_data['user_phone']
            verification_code = PhoneVerificationCode()._generate_phone_verification_number()

            verification_msg = ('Hello! We are the SogangDjango Project! ',
                                'to register your phone number type in the following ',
                                f'verification code: {verification_code}')
            phone_message_sender.send_message(
                to=user_phone, body=''.join(verification_msg))

            reset_data = PhoneVerificationCode(
                user_phone=user_phone,
                verification_code=verification_code)
            reset_data.full_clean()
            reset_data.save()
            return redirect(reverse_lazy('auth:auth_phone_verify_code'))
        else:
            context = dict(auth_phone_only_form=auth_phone_only_form)
            return render(request, 'auth/send_phone_verification_code.html',
                          context)
    if request.method == "GET":
        auth_phone_only_form = AuthPhoneOnlyVerificationForm()
        return render(request,
                      'auth/send_phone_verification_code.html',
                      {'auth_phone_only_form': auth_phone_only_form}
                      )

################################################
################################################
#              Account Activation
################################################
################################################


def auth_activation_confirm_view(request, uidb64, token):
    if request.method == "GET":
        auth_logout(request)
        confirming_user = get_object_or_404(
            User, id=urlsafe_base64_decode(uidb64))

        verification_query = EmailVerificationCode.objects.filter(
            email=confirming_user.email)

        if verification_query.exists():
            verification_model = verification_query.latest('created')
            if verification_model.verification_code_matches(token):
                if verification_model.is_not_expired:
                    confirming_user.is_active = True
                    confirming_user.save()
                    return redirect(reverse_lazy('auth:form_successful',
                                                 kwargs={'label': 'account_activated'}))
                else:
                    return redirect(reverse_lazy('auth:form_unsuccessful',
                                                 kwargs={'label': 'email_activation_timeout'}))

        return redirect(reverse_lazy('auth:form_unsuccessful',
                                     kwargs={'label': 'email_activation_invalid'}))
    else:
        return HttpResponse(status=403)


################################################
################################################
#         Auth success, unsuccess view
################################################
################################################


def auth_form_unsuccessful_view(request, label):
    auth_logout(request)
    if label == 'email_activation_timeout':
        fail_msg = (
            'Your account activation code as expired! ',
            'Request another email verification code!'
        )
    elif label == 'email_activation_code_invalid':
        fail_msg = (
            'Your activation code is invalid! ',
            'Request another email verification code!'
        )
    else:
        return HttpResponse(status=404)

    context = dict(fail_msg=fail_msg)
    return render(request, 'auth/form_success.html', context)


def auth_form_successful_view(request, label):
    auth_logout(request)
    if label == 'user_register':
        success_msg = (
            'You have sucessfully registered your account! ',
            'Activate your account with the link we provided to your email!'
        )
    elif label == 'password_reset_email_sent':
        success_msg = (
            'We have sent your password reset link to your email!',
            'Reset with the link provided from our email!'
        )
    elif label == 'register_phonenumber' or label == 'change_phonenumber':
        success_msg = (
            'You have sucessfully registered your phone number! ',
            'Please log in again'
        )
    elif label == 'change_email':
        success_msg = (
            'You have sucessfully registered your email! ',
            'Activate your account with the link we provided to your email!'
        )
    elif label == 'password_change_complete':
        success_msg = (
            'You have successfully changed your password!',
            'Please log in again')
    elif label == 'account_activated':
        success_msg = (
            'Your account has been activated!',
            'Please log in again')
    else:
        return HttpResponse(status=404)

    context = dict(success_msg=success_msg)
    return render(request, 'auth/form_success.html', context)

"""
                if "Register" in request.POST:
                    uid = urlsafe_base64_encode(force_bytes(user_object.pk))
                    token = default_token_generator.make_token(user_object)
                    return redirect(reverse_lazy('auth:password_reset_confirm',
                                                 kwargs={'uidb64': uid, 'token': token}))
                elif "Register" in request.POST:
                    if User.objects.filter(user_phone=user_phone).exists():
                        auth_phone_verification_form.add_error(
                            user_phone, "The phone number is already being used")
                        return render(request,
                                      'auth/verify_phone_code.html',
                                      {'auth_phone_verification_form': auth_phone_verification_form}
                                      )
                    else:
                        user_object.user_phone = user_phone
                        user_object.save()
                        return redirect(reverse_lazy('auth:form_successful',
                                                     kwargs={'label': 'register_phonenumber'}))
"""