from django.conf import settings
from django.db import models


from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _


USER_MODEL = get_user_model()


class CheckedToken(models.Model):
    """
    Stores the used tokens for safety-checking purposes.
    """
    token = models.CharField(max_length=300)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        ordering = ('-timestamp', 'user__username')

    def __unicode__(self):
        return '{0} - {1}, {2}'.format(
            self.token, self.timestamp, self.user.username)


class TestUser(USER_MODEL):
    remote_id = models.CharField(_('remote_id'),
                                 max_length=75,
                                 blank=True,
                                 null=True)
