from django import forms
from django.contrib import admin
from .models import UserProfile



class UserProfileform(forms.ModelForm):
	user_picture = forms.ImageField(
		help_text="Upload image: ", 
		required=False)
	user_description = forms.CharField(
		max_length=500, 
		widget=forms.TextInput(
			attrs={'class':'form-control','placeholder':'Write whatever about you',
			'size':'30'}))
	class Meta:
	  	model = UserProfile
	  	fields = ('user_picture','user_description')



        
      