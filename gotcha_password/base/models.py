from __future__ import unicode_literals

from django.core import validators
from django.db import models
from django.utils.crypto import constant_time_compare

from random import SystemRandom
from os import urandom
from datetime import time

from base.utils import get_random_seed, hash_password, list_permutations

# going to use our own User class
class User(models.Model):
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text='Required. 30 characters or fewer. Letters and digits only.',
        validators=[
            validators.RegexValidator(
                r'^\w+$',
                'Enter a valid username. This value may contain only letters and numbers.'
            ),
        ],
        error_messages={
            'unique': 'A user with that username already exists.',
        },
    )
    password = models.CharField(max_length=128)
    # seed for Extract function
    seed = models.CharField(max_length=12)
    num_images = models.PositiveSmallIntegerField()
    # storing permutation for research purposes
    permutation = models.CharField(max_length=50)

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
            hashed = hash_password(raw_password, salt, p)
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
    Model representing each login attempt into the site and various statistics for the login
    attempt. Stores the password resulting from hashing the raw password once and the permutation
    sent for this login attempt.
    """
    user = models.ForeignKey(User)
    right_password = models.BooleanField()
    correct_images = models.PositiveSmallIntegerField()
    raw_password = models.CharField(max_length=128) # not actually raw password, hashed once
    permutation = models.CharField(max_length=50)

    def timed_check_password(self, threshold, iterations):
        """
        Returns the number of seconds it takes to check if this password is correct, with the
        given parameters.
        """
        start = time.time()

        salt, password = self.user.password.split('$')
        for p in list_permutations(permutation, self.user.num_images, threshold=threshold):
            # iterations - 1 because raw_password already hashed once
            hashed = hash_password(self.raw_password, salt, p, iterations=iterations - 1)
            if constant_time_compare(hashed, password):
                break

        return time.time() - start
