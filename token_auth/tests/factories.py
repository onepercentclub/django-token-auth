import datetime
import factory

from django.utils import timezone

from token_auth.models import CheckedToken
from token_auth.tests.models import TestUser


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = TestUser

    username = 'rterkuile'
    first_name = 'Renko'
    last_name = 'ter Kuile'
    email = 'renko.terkuile@example.com'
    remote_id = 'renko@gmail.com'
    is_active = True


class CheckedTokenFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CheckedToken

    token = '7baTf5AVWkpkiACH6nNZZUVzZR0rye7rbiqrm3Qrgph5Sn3EwsFERytBwoj2aqS' \
            'dISPvvc7aefusFmHDXAJbwLvCJ3N73x4whT7XPiJz7kfrFKYal6WlD8lu5JZgVT' \
            'mV5hdywGQkPMFT1Z7m4z1ga6Oud2KoQNhrf5cKzQ5CSdTojZmZ0FT24jBuwm5YU' \
            'qFbvwTBxg=='
    timestamp = datetime.datetime(2012, 12, 18, 11, 51, 15).replace(
        tzinfo=timezone.get_current_timezone())
    user = factory.SubFactory(UserFactory)
