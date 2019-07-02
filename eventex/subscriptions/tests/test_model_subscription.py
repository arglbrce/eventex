from datetime import datetime

from django.test import TestCase

from eventex.subscriptions.models import Subscription


class SubscriptionModelTest(TestCase):
    def setUp(self):
        self.obj = Subscription(
            name='Allan Reffson',
            cpf='45773653320',
            email='arglbr@gmail.com',
            phone='85-988728779'
        )
        self.obj.save()

    def test_create(self):
        self.assertTrue(Subscription.objects.exists())

    def test_created_at(self):
        """Subscription must have an auto created_at attr."""
        self.assertIsInstance(self.obj.created_at, datetime)

    def test_str(self):
        self.assertEqual('Allan Reffson', str(self.obj))
