from django.http import JsonResponse

# django basic tools
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _


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

from ..models import PhoneVerificationCode, EmailVerificationCode
from ..forms import (
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
#         Check Email and Phone exists
################################################
################################################


def check_email_exists_api_view(request):
    if request.is_ajax():
        email_to_check = request.method.GET.get('email', None)
    if email_to_check:
        data = dict(email_exists=User.objects.filter(
            email__iexact=email_to_check)
        )
        return JsonResponse(data)


def check_phone_exists_api_view(request):
    if request.is_ajax():
        user_phone_to_check = request.method.GET.get('user_phone', None)
    if user_phone_to_check:
        data = dict(user_phone_exists=User.objects.filter(
            user_phone__iexact=user_phone_to_check)
        )
        return JsonResponse(data)

################################################
################################################
#         Send verification code
################################################
################################################


@sensitive_post_parameters()
def auth_phone_send_verification_code_api_view(request):
    # Unallow methods without Post or XHLHttpRequest
    if request.method != "POST" and not request.is_ajax():
        return JsonResponse(status=400)

    auth_phone_only_form = AuthPhoneOnlyVerificationForm(request.POST)
    if auth_phone_only_form.is_valid():
        user_phone = auth_phone_only_form.cleaned_data["user_phone"]

        # Check if it is required to have phone number registered!
        if request.POST.dict().get("check_phone_number_exists", None) == "true":
            phone_exists = User.objects.filter(
                user_phone__exact=user_phone).exists()
            if phone_exists == False:
                phone_exists_msg = _("Phone number is not registered")
                auth_phone_only_form.add_error("user_phone", phone_exists_msg)
                data = dict(code_sent=False,
                            errors=auth_phone_only_form.errors.as_json())
                return JsonResponse(data, status=200, safe=False)

        # Generate verification code
        verification_code = PhoneVerificationCode()._generate_phone_verification_number()

        verification_msg = (
            'Hello! You have requested for the verification code for the SogangDjango \
            Project! ',
            f'Verification code: {verification_code}')

        # Save verification code with phone number
        phone_verification_data = PhoneVerificationCode(
            user_phone=user_phone,
            verification_code=verification_code)
        phone_verification_data.save()

        # The ajax checks for "code_sent" to be true or false
        # It will display invalid field when false
        data = dict(code_sent=True)
        phone_message_sender.send_message(
            to=user_phone, body=''.join(verification_msg))
        return JsonResponse(data, status=200)
    else:
        data = dict(code_sent=False,
                    errors=auth_phone_only_form.errors.as_json())
        return JsonResponse(data, status=200, safe=False)


@sensitive_post_parameters()
def phone_verify_api_view(request):
    # Unallow methods without Post or XHLHttpRequest
    if request.method != "POST" and not request.is_ajax():
        return JsonResponse(status=400)

    auth_phone_verification_form = AuthPhoneVerificationForm(request.POST)
    if auth_phone_verification_form.is_valid():
        user_phone = auth_phone_verification_form.cleaned_data[
            'user_phone']
        # Check if it is required to have phone number registered!
        if request.POST.dict().get("check_phone_number_exists", None) == "true":
            phone_exists = User.objects.filter(
                user_phone__exact=user_phone).exists()
            if phone_exists == False:
                phone_exists_msg = _("Phone number is not registered")
                auth_phone_only_form.add_error(
                    "user_phone", phone_exists_msg)
                data = dict(code_sent=False,
                            errors=auth_phone_only_form.errors.as_json())
                return JsonResponse(data, status=200, safe=False)

            verification_code = auth_phone_verification_form.cleaned_data[
                'verification_code']

            latest_of_user_reset_data = PhoneVerificationCode.objects.filter(
                user_phone=user_phone).latest('created')

            # Check whether object exists or not before calling class methods
            if latest_of_user_reset_data:
                # Check if the verification code is expired or not
                if not latest_of_user_reset_data.is_not_expired:
                    auth_phone_verification_form.add_error(
                        "verification_code", "Your key has expired")
                    data = dict(
                        verification_success=False,
                        errors=auth_phone_verification_form.errors.as_json()
                    )
                    return JsonResponse(data, status=200)
                # Then check whether the verification code matches with the
                # latest code
                if not latest_of_user_reset_data.verification_code_matches(verification_code):
                    auth_phone_verification_form.add_error(
                        "verification_code", "Incorrect verification code")
                    data = dict(
                        verification_success=False,
                        errors=auth_phone_verification_form.errors.as_json()
                    )
                    return JsonResponse(data, status=200)
                # Then redirect the user to the password change form with token
                # urls
                user_object = User.objects.get(user_phone=user_phone)
                uid = urlsafe_base64_encode(force_bytes(user_object.pk))
                token = default_token_generator.make_token(user_object)
                data = dict(redirect=reverse_lazy('auth:password_reset_confirm',
                                                  kwargs={'uidb64': uid, 'token': token}))
                return JsonResponse(data, status=302)
    else:
        auth_phone_verification_form.add_error(
            None, _("Invalid phone number or verification code")
        )
        data = dict(
            verification_success=False,
            errors=auth_phone_verification_form.errors.as_json()
        )
        return JsonResponse(data, status=200)


################################################
################################################
#           Email Password Reset
################################################
################################################


# from django.contrib.auth views but needs some changing

def email_password_reset_api_view(request,
                                  email_template_name='auth/email/email_content_password_reset.html',
                                  subject_template_name='auth/email/password_reset_subject.txt',
                                  password_reset_form=PasswordResetForm,
                                  token_generator=default_token_generator,
                                  post_reset_redirect=None,
                                  from_email="sogangdjango@noreply.com",
                                  extra_context=None,
                                  html_email_template_name=None,
                                  extra_email_context=None):
    if request.method != "POST" and not request.method.is_ajax():
        return JsonResponse(status=400)

    if post_reset_redirect is None:
        post_reset_redirect = reverse_lazy('auth:form_successful', kwargs={
                                           "label": "password_reset_email_sent"})
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)

    form = password_reset_form(request.POST)
    if form.is_valid():

        email = form.cleaned_data['email']

        if request.POST.dict().get("check_email_exists", None) == "true":
            email_exists = User.objects.filter(
                email__exact=email).exists()
            if email_exists == False:
                email_exists_msg = _("Email is not registered")
                form.add_error(
                    "email", email_exists_msg)
                data = dict(email_sent=False,
                            errors=form.errors.as_json())
                return JsonResponse(data, status=200, safe=False)

        opts = {
            'use_https': request.is_secure(),
            'token_generator': token_generator,
            'from_email': from_email,
            'email_template_name': email_template_name,
            'subject_template_name': subject_template_name,
            'request': request,
            'html_email_template_name': html_email_template_name,
            'extra_email_context': extra_email_context,
        }
        form.save(**opts)
        data = dict(redirect=post_reset_redirect)
        return JsonResponse(data, status=302)

    else:
        data = dict(email_sent=False,
                    errors=form.errors.as_json())
        JsonResponse(data, status=200, safe=False)


################################################
################################################
#              Basic Auth
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
                                                       user_type=10)

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
        context = dict(
            password_reset_form=password_reset_form,
            phone_verification_send_form=phone_verification_send_form)
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
        'label': 'email_password_reset'})


class AuthPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    token_generator = default_token_generator
    success_url = reverse_lazy('auth:form_successful', kwargs={
        'label': 'password_change_complete'})


################################################
################################################
#              Phone Registration
################################################
################################################

@sensitive_post_parameters()
def auth_phone_verify_code_view(request):
    if request.method == "POST":
        auth_phone_verification_form = AuthPhoneVerificationForm(request.POST)
        if auth_phone_verification_form.is_valid():
            user_phone = auth_phone_verification_form.cleaned_data[
                'user_phone']

            verification_code = auth_phone_verification_form.cleaned_data[
                'verification_code']

            latest_of_user_reset_data = PhoneVerificationCode.objects.filter(
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
    elif label == 'email_password_reset':
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