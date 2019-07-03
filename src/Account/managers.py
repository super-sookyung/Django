from django.db import models
from .utils import random_string_generator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):

    def create_user(self, email, user_type, slug_name_for_url=None, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        slug_name_for_url = random_string_generator(size=10)

        # this is meant to prevent the one in a million chance of the same slug
        # being created!
        if self.filter(slug_name_for_url__exact=slug_name_for_url).exists():
            slug_name_for_url = slug_name_for_url \
                + random_string_generator(size=3)
    

        user = self.model(
            email=self.normalize_email(email),
            slug_name_for_url=slug_name_for_url,
        )
        user.user_type = user_type

        user.set_password(password)
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, slug_name_for_url, user_type, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            slug_name_for_url=slug_name_for_url,
        )
        user.user_type = user_type
        user.is_active = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, slug_name_for_url, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
            slug_name_for_url=slug_name_for_url,
            user_type = 50
        )
        # user.user_type = 50
        user.admin = True
        user.is_active = True
        user.save(using=self._db)
        return user