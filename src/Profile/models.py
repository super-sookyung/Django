from django.db import models
	
from django.conf import settings

from PhoneEmail.fields import PhoneNumberField

User = settings.AUTH_USER_MODEL


class UserProfile(models.Model):
    user_id = models.OneToOneField(
        User, on_delete=models.CASCADE)
    user_picture = models.ImageField(
        upload_to='profile_pics', blank=True, null=True)
    user_description = models.CharField(max_length=500)


class GroupProfile(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    user_picture = models.ImageField(upload_to='profile_pics')
    user_description = models.CharField(max_length=500)