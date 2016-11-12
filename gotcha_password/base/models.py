from __future__ import unicode_literals

from django.core import validators, signing
from django.db import models
from django.utils.crypto import constant_time_compare

from random import SystemRandom
from os import urandom
from datetime import time

from base.utils import *

class UserManager(models.Manager):
    def create(self, username, raw_password, seed, num_images, labels):
        password, permutation = make_password(raw_password, labels)

        user = super(UserManager, self).create(
            username=username,
            password=password,
            seed=seed,
            num_images=num_images,
            permutation=','.join(map(str, permutation)),
        )

        # renumber labels so that choosing the same order of labels later
        # will return the correct permutation
        for i, num in enumerate(permutation):
            Label.objects.create(user=user, number=num, text=labels[i])

        return user

# going to use our own User class
class User(models.Model):
    objects = UserManager()

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
    # random number of images, from 3 to 7
    num_images = models.PositiveSmallIntegerField()
    # storing permutation for research purposes
    permutation = models.CharField(max_length=50)

    def __unicode__(self):
        return self.username

    def get_salt(self):
        return self.password.split('$')[0]

    def get_permutation(self):
        return map(int, self.permutation.split(','))

    def set_password(self, raw_password, labels):
        password, permutation = make_password(raw_password, labels)

        self.password = password
        self.permutation = ','.join(map(str, permutation))

        for i, num in enumerate(permutation):
            self.labels.filter(number=num).update(text=labels[i])

    def check_password(self, raw_password, permutation):
        """
        Returns True if the given password and the ordered list of labels match the
        stored password hash.
        """
        # in a true implementation, this would list all of the possibilities that are
        # wrong within a certain threshold. instead of allowing wrong images, this
        # will check for exact correctness
        hashed = hash_password(raw_password, self.get_salt(), permutation)
        return constant_time_compare(hashed, self.password)

class Label(models.Model):
    """
    A label for an image sent to the user. User will create labels when they
    create an account and labels will be sent back on log in to match with images.
    """
    class Meta:
        ordering = ['user', 'number']

    user = models.ForeignKey(User, related_name='labels')
    # range [0, user.num_images) representing the order of this label in the list of labels for the user
    number = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=255)

    def __unicode__(self):
        text = self.text
        if len(text) > 13:
            text = '%s...' % text[:10]

        return '%s #%d (%s)' % (self.user.username, self.number, text)

class LoginAttempt(models.Model):
    """
    Model representing each login attempt into the site and various statistics for the login
    attempt. Stores the password resulting from hashing the raw password once and the permutation
    sent for this login attempt.
    """
    user = models.ForeignKey(User)
    right_password = models.BooleanField()
    correct_images = models.PositiveSmallIntegerField()
    password = models.CharField(max_length=128) # the password the user used to log in again, encrypted
    permutation = models.CharField(max_length=50)

    @staticmethod
    def encode(password):
        return signing.dumps(password, salt='login_attempt')

    def __unicode__(self):
        if self.right_password:
            percentage = float(self.correct_images) / self.user.num_images * 100
            text = '%0.1f%' % percentage
        else:
            text = 'invalid'
        return '%s (%s)' % (self.user.username, text)

    def get_permutation(self):
        return map(int, self.permutation.split(','))

    def timed_check_password(self, threshold, iterations):
        """
        Returns the number of seconds it takes to check if this password is correct, with the
        given parameters.
        """
        start = time.time()
        salt = self.user.get_salt()
        password = signing.loads(self.password, salt='login_attempt')
        # iterations - 1, because raw_password already hashed once
        iterations -= 1

        for p in list_permutations(self.get_permutation(), self.user.num_images, threshold=threshold):
            hashed = hash_password(password, salt, p, iterations=iterations)
            if constant_time_compare(hashed, self.user.password):
                break

        return time.time() - start
