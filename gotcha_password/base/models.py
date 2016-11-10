from __future__ import unicode_literals

from django.core import validators
from django.db import models
from django.utils.crypto import pbkdf2

from random import SystemRandom
from os import urandom

from base.utils import *

# going to use our own User class
class User(models.Model):
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.',
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$',
                _('Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.')
            ),
        ],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    password = models.CharField(
        max_length=16, # cap password at 16 characters for research purposes
    )
    # seed for Extract function
    seed = models.PositiveIntegerField()
    num_images = models.SmallPositiveIntegerField()

    def hash_password(self, raw_password, salt, permutation):
        """
        Hash data of the form "<raw_password>$<comma sep permutations>"
        """
        password = '%s$%s' % (raw_password, ','.join(permutation))
        hashed = pbkdf2(password, salt, 1000)
        return '%d$%s' % (salt, hashed)

    def set_password(self, raw_password, labels):
        """
        Hashes and stores the user's password with the given parameters. Still
        needs to call .save()
        """
        salt = get_random_seed()
        permutation = range(len(labels))
        SystemRandom().shuffle(permutation)

        self.password = self.hash_password(raw_password, salt, permutation)

    def check_password(self, raw_password, permutation):
        """
        Returns True if the given password and label permutation match the
        stored password hash.
        """
        salt, password = self.password.split('$')
        hashed = self.hash_password(raw_password, salt, permutation)
        return hashed == password

class Label(models.Model):
    """
    A label for an image sent to the user. User will create labels when they
    create an account and labels will be sent back on log in to match with images.
    """
    user = models.ForeignKey(User)
    text = models.CharField(max_length=255)
