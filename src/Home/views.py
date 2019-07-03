from django.shortcuts import render

from Auth.forms import (
    UserRegistrationForm, AuthPhoneVerificationForm,
    AuthPhoneOnlyVerificationForm, UserAuthenticationForm
)


def homepage_view(request):
    if not request.user.is_authenticated():
        registration_form = UserRegistrationForm()
        login_form = UserAuthenticationForm()
        context = dict(
            registration_form=registration_form,
            login_form=login_form
        )
        return render(request, 'home/landing.html', context)
    else:
        return render(request, 'home/home.html', dict())