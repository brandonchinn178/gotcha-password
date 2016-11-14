from django.test import TestCase

from base.models import *
from base.utils import *

class UserTestCase(TestCase):
    def _create_user(self, **kwargs):
        defaults = {
            'username': 'test',
            'email': 'test@example.com',
            'raw_password': 'password',
            'seed': get_random_seed(),
            'num_images': 3,
            'labels': ['a', 'b', 'c'],
        }
        defaults.update(kwargs)
        return User.objects.create(**defaults)

    def test_create(self):
        user = self._create_user()

        label_objects = Label.objects.filter(user=user)
        permutation = [
            label_objects.get(text='a').number,
            label_objects.get(text='b').number,
            label_objects.get(text='c').number,
        ]
        self.assertEqual(permutation, user.get_permutation())

    def test_set_password(self):
        pass

    def test_check_password(self):
        user = self._create_user()
        self.assertTrue(user.check_password('password', user.get_permutation()))

class LoginAttemptTestCase(TestCase):
    def test_timed_check(self):
        pass
