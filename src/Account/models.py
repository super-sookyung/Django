from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _

from PhoneEmail.fields import PhoneNumberField

from .managers import UserManager


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name=_('email address'), max_length=255,
        null=False, unique=True, db_index=True
    )

    USER_TYPES = (
        (1, 'Normal User'),
        (2, 'Group User'),
        (10, 'Staff with no delete Authority'),
        (20, 'Staff with Authority up to Post delete'),
        (30, 'Staff with Authority up to User delete'),
        (50, 'Admin'),
    )

    user_phone = PhoneNumberField(
        null=False, db_index=True, max_length=16)

    admin = models.BooleanField(
        _('is admin'), default=False)

    user_type = models.PositiveSmallIntegerField(
        _('user type'), choices=USER_TYPES, default=1)

    is_active = models.BooleanField(
        _('is active'), default=False)

    slug_name_for_url = models.CharField(
        _('unique name for your url link'),
        max_length=30, db_index=True, unique=True, blank=False, null=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['slug_name_for_url', ]

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.slug_name_for_url

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return "email: %s, slug_name_for_url: %s" % (self.email, self.slug_name_for_url)

    @property
    def is_staff(self):
        return self.user_type in (20, 30, 40, 50)

    @property
    def is_admin(self):
        return self.admin