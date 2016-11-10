from __future__ import unicode_literals

from django.core import validators
from django.db import models
from django.utils.crypto import pbkdf2, constant_time_compare

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
                'Enter a valid username. This value may contain only '
                  'letters, numbers ' 'and @/./+/-/_ characters.'
            ),
        ],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    password = models.CharField(max_length=128)
    # seed for Extract function
    seed = models.CharField(max_length=12)
    num_images = models.PositiveSmallIntegerField()
    # storing permutation for research purposes
    permutation = models.CharField(max_length=50)

    def hash_password(self, raw_password, salt, permutation):
        """
        Hash data of the form "<raw_password>$<comma sep permutations>"
        """
        password = '%s$%s' % (raw_password, ','.join(permutation))
        hashed = pbkdf2(password, salt, HASH_ITERATIONS)
        return '%s$%s' % (salt, hashed)

    def set_password(self, raw_password, labels):
        """
        Hashes and stores the user's password with the given parameters. Still
        needs to call .save()
        """
        salt = get_random_seed()
        permutation = [l.number for l in labels]
        SystemRandom().shuffle(permutation)

        self.permutation = permutation
        self.password = self.hash_password(raw_password, salt, permutation)

    def check_password(self, raw_password, labels):
        """
        Returns True if the given password and the ordered list of labels match the
        stored password hash.

        NOTE: will not be used in this implementation. Left here as a proof of concept.
        """
        salt, password = self.password.split('$')
        permutation = [l.number for l in labels]

        for p in list_permutations(permutation, self.num_images):
            hashed = self.hash_password(raw_password, salt, p)
            if constant_time_compare(hashed, password):
                return True

        return False

class Label(models.Model):
    """
    A label for an image sent to the user. User will create labels when they
    create an account and labels will be sent back on log in to match with images.
    """
    class Meta:
        ordering = ['user', 'number']

    user = models.ForeignKey(User)
    # range [0, user.num_images) representing the order of this label in the list of labels for the user
    number = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=255)

class LoginAttempt(models.Model):
    """
    Model representing each login attempt into the site and various statistics for the login attempt
    """
    user = models.ForeignKey(User)
    right_password = models.BooleanField()
    correct_images = models.PositiveSmallIntegerField()
