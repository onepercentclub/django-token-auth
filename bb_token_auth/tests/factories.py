import datetime
import factory

from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import CheckedToken

AUTH_USER_MODEL = get_user_model()


class BlueBottleUserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = AUTH_USER_MODEL

    username = 'rterkuile'
    first_name = 'Renko'
    last_name = 'ter Kuile'
    email = 'renko.terkuile@booking.com'


class CheckedTokenFactory(factory.DjangoModelFactory):
    FACTORY_FOR = CheckedToken

    # REMINDER: This token was built using 'bbbbbbbbbbbbbbbb' as HMAC key.
    #BookingSeleniumTestCase Keep that in mind when writing unit tests using this factory model.
    token = '7baTf5AVWkpkiACH6nNZZUVzZR0rye7rbiqrm3Qrgph5Sn3EwsFERytBwoj2aqS' \
            'dISPvvc7aefusFmHDXAJbwLvCJ3N73x4whT7XPiJz7kfrFKYal6WlD8lu5JZgVT' \
            'mV5hdywGQkPMFT1Z7m4z1ga6Oud2KoQNhrf5cKzQ5CSdTojZmZ0FT24jBuwm5YU' \
            'qFbvwTBxg=='
    timestamp = datetime.datetime(2012, 12, 18, 11, 51, 15).replace(
        tzinfo=timezone.get_current_timezone())
    user = factory.SubFactory(BlueBottleUserFactory)