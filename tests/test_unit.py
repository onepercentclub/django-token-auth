from decimal import Decimal

from django.template import Template, Context, TemplateSyntaxError
from django.utils import unittest, timezone

from bb_salesforce.mappings import (CropMapping, ConcatenateMapping,
                                    EmailMapping,EuroMapping)
from bb_salesforce.transformers import MemberTransformer

from tests.factories import MemberFactory, AddressFactory, CountryFactory
from tests.models import Member


class MappingsTestCase(unittest.TestCase):

    def setUp(self):
        self.member1 = MemberFactory.create(
            username='Vlammetje', first_name='Henk',last_name='Wijngaarden',
            email='henk@vlamindepijp.nl', budget=Decimal(15.5),
            gender='m')

        self.member2 = MemberFactory.create(
            username='H\x543nk', first_name='Hank',last_name=None,
            email='henk#vlamindepijp.nl')

    def test_crop_mapping(self):
        mapping = CropMapping('username', 4)
        mapped = mapping(self.member1).to_field()
        self.assertEqual(mapped, 'Vlam')

    def test_concat_mapping(self):
        mapping = ConcatenateMapping(['last_name', 'first_name'],
                                      concatenate_str=', ')
        mapped = mapping(self.member1).to_field()
        self.assertEqual(mapped, 'Wijngaarden, Henk')

    def test_email_mapping(self):
        # Check that valid email address gets parsed
        mapping = EmailMapping('email')
        mapped = mapping(self.member1).to_field()
        self.assertEqual(mapped, 'henk@vlamindepijp.nl')
        # Now try a user with no valid email address
        mapping = EmailMapping('email')
        mapped = mapping(self.member2).to_field()
        self.assertEqual(mapped, '')

    def test_euro_mapping(self):
        mapping = EuroMapping('budget')
        mapped = mapping(self.member1).to_field()
        self.assertEqual(mapped, '15.50')

        mapping = EuroMapping('budget')
        mapped = mapping(self.member2).to_field()
        self.assertEqual(mapped, '0.00')


class TransformerTestCase(unittest.TestCase):

    def setUp(self):
        self.time = timezone.datetime(2015, 1, 1)
        self.time_flat = '2015-01-01T00:00:00.000Z'

        self.member1 = MemberFactory.create(
            username='Vlammetje', first_name='Henk',last_name='Wijngaarden',
            email='henk@vlamindepijp.nl', budget=Decimal(15.5),
            gender='m',
            member_since=self.time,
            last_login=self.time,
            date_joined=self.time,
            deleted=None
            )

        self.address = AddressFactory(
            user=self.member1,
            line1='Paleis',
            line2='Dam 1',
            postal_code='1000AA',
            state='',
            city='Nul Twintig',
            country=CountryFactory(name='Netherlands')
            )

        self.maxDiff = None



    def test_member_transformer(self):
        transformer = MemberTransformer(self.member1)
        value_dict = transformer.to_dict()

        data = {'category1': u'',
                'last_name': 'Wijngaarden',
                'about_me_us': u'',
                'external_id': 9,
                'member_since': self.time,
                'is_active': False,
                'bank_account_city': '',
                'phone': u'',
                'primary_language': u'',
                'has_activated': False,
                'mailing_city': 'Nul Twintig',
                'date_joined': self.time,
                'first_name': 'Henk',
                'receive_newsletter': True,
                'mailing_state': '',
                'gender': u'Male',
                'bank_account_holder': '',
                'mailing_street': u'Paleis Dam 1',
                'mailing_postal_code': '1000AA',
                'mailing_country': 'Netherlands',
                'picture_location': '',
                'bank_account_iban': '',
                'bank_account_active_recurring_debit': '',
                'last_login': self.time,
                'location': u'',
                'birth_date': None,
                'user_name': u'Vlammetje',
                'email': 'henk@vlamindepijp.nl'}

        # Try transform to_field
        self.assertEqual(data, value_dict)

        value_list = transformer.to_csv()

        data = ['Wijngaarden',
                '',
                '0',
                self.time_flat,
                'Henk',
                '',
                'Paleis Dam 1',
                'Netherlands',
                '1',
                '',
                self.time_flat,
                '',
                'Vlammetje',
                'henk@vlamindepijp.nl',
                '',
                '',
                self.time_flat,
                '0',
                '',
                '',
                'Male',
                '',
                '',
                '1000AA',
                '',
                'Nul Twintig',
                '',
                '9']

        # Try transform to_csv
        self.assertEqual(data, value_list)
