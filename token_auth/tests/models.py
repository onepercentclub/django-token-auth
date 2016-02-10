from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
import token_auth.models

USER_MODEL = get_user_model()


class TestUser(USER_MODEL):
    remote_id = models.CharField(_('remote_id'),
                                 max_length=75,
                                 blank=True,
                                 null=True)

token_auth.models.TestUser = TestUser
