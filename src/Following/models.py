from django.db import models
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

# for translation

User = settings.AUTH_USER_MODEL

class Following(models.Model):
    follower = models.ForeignKey(
        User, related_name="follower", db_index=True, on_delete=models.CASCADE)
    followed = models.ForeignKey(
    	User, related_name="followed", db_index=True, on_delete=models.CASCADE)
    following_since = models.DateTimeField(
    	auto_now_add=True)
    blocked = models.BooleanField(
    	default=False)

    class Meta:
    	unique_together = (("follower", "followed"))
    def __str__(self):
        return f'{self.follower}:{self.followed}:{self.following_since}'