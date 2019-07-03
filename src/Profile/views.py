from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileform
from django.views.decorators.http import require_http_methods

# Create your views here.
@login_required
def create_profile_view(request):
	if request.method == "POST":
		form = UserProfileform(request.POST)
		userprofile=Userprofile(
			user_id= request.user.id,
			user_description= form.cleaned_data['user_description'],
			user_picture= form.cleaned_data['user_picture']
			)
		userprofile.save()
	else :
		form = HttpResponse(status=400)
	return render(request,'profile/create.html', {'form': form})

