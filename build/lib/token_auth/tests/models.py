from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
import token_auth.models


class TestUser(AbstractBaseUser):
    email = models.CharField(max_length=50)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    remote_id = models.CharField(_('remote_id'), max_length=75, blank=True, null=True)

token_auth.models.TestUser = TestUser
