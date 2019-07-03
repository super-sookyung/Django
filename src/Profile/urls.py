from django.conf.urls import url, include

from . import views

from django.urls import reverse

urlpatterns = [
	url(r'^create/$',views.create_profile_view, name = "create"),
	]
	
