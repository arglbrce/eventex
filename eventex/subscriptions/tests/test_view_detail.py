import hashlib

from django.test import TestCase

from eventex.subscriptions.models import Subscription


class SubscriptionDetailGet(TestCase):
    def setUp(self):
        email = 'arglbr@gmail.com'
        hash_url = hashlib.md5(email.encode()).hexdigest()
        
        self.obj = Subscription.objects.create(
            name='Allan Reffson',
            cpf='45773653320',
            email=email,
            phone='85-988728779',
            hash_url=hash_url
        )

        self.resp = self.client.get(f'/inscricao/{self.obj.hash_url}/')

    def test_get(self):
        self.assertEqual(200, self.resp.status_code)

    def test_template(self):
        self.assertTemplateUsed(
            self.resp, 'subscriptions/subscription_detail.html')

    def test_context(self):
        subscription = self.resp.context['subscription']
        self.assertIsInstance(subscription, Subscription)

    def test_html(self):
        contents = (self.obj.name, self.obj.cpf,
                    self.obj.email, self.obj.phone)
        with self.subTest():
            for expected in contents:
                self.assertContains(self.resp, expected)


class SubscriptionDetailNotFound(TestCase):
    def test_not_found(self):
        resp = self.client.get('/inscricao/0/')
        self.assertEqual(404, resp.status_code)