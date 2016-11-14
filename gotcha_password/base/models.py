from __future__ import unicode_literals

from django.core import validators
from django.core.files.base import ContentFile
from django.db import models
from django.utils.crypto import constant_time_compare

import time, json
from itertools import permutations

from base.utils import *

class UserManager(models.Manager):
    def create(self, username, email, raw_password, seed, num_images, labels):
        password, salt, permutation = make_password(raw_password, labels)

        user = super(UserManager, self).create(
            username=username,
            email=email,
            password=password,
            salt=salt,
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
        help_text='30 characters or fewer. Letters and digits only.',
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
    email = models.EmailField(help_text='Will only be used for communications about this study.')
    # stores just the raw password hashed one time (without salt or permutation)
    password = models.CharField(max_length=128)
    salt = models.CharField(max_length=12)
    # seed for Extract function
    seed = models.CharField(max_length=12)
    # random number of images, from 3 to 7
    num_images = models.PositiveSmallIntegerField()
    # storing permutation for research purposes
    permutation = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.username

    def get_permutation(self):
        return map(int, self.permutation.split(','))

    def set_password(self, raw_password, labels):
        self.password, self.salt, permutation = make_password(raw_password, labels)
        self.permutation = ','.join(map(str, permutation))

        for i, num in enumerate(permutation):
            self.labels.filter(number=num).update(text=labels[i])

    def get_hashed_password(self, iterations=HASH_ITERATIONS):
        permutation = self.get_permutation()
        return hash_password(self.password, self.salt, permutation, iterations)

    def check_password(self, raw_password, permutation):
        """
        Returns True if the given password and the ordered list of labels match the
        stored password hash.
        """
        # in a true implementation, this would list all of the possibilities that are
        # wrong within a certain threshold. instead of allowing wrong images, this
        # will check for exact correctness
        hashed_once = hash_once(raw_password, self.salt)
        hashed = hash_password(hashed_once, self.salt, permutation)
        password = self.get_hashed_password()
        return constant_time_compare(hashed, password)

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
    user = models.ForeignKey(User, related_name='logins')
    right_password = models.BooleanField()
    correct_images = models.PositiveSmallIntegerField()
    password = models.CharField(max_length=128) # the password the user used to log in again, encrypted
    permutation = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    # holds results of benchmarking for this login attempt
    benchmarks = models.FileField(upload_to='benchmarks', null=True)

    def __unicode__(self):
        if self.right_password:
            percentage = float(self.correct_images) / self.user.num_images * 100
            text = '%0.1f%%' % percentage
        else:
            text = 'invalid'
        return '%s (%s)' % (self.user.username, text)

    def get_permutation(self):
        return map(int, self.permutation.split(','))

    def set_benchmarks(self, benchmarks):
        benchmarks = json.dumps(benchmarks)
        filename = '%s_%s.json' % (
            self.user.username, self.timestamp.strftime('%m_%d_%Y_%H:%M:%S')
        )
        self.benchmarks.delete()
        self.benchmarks.save(filename, ContentFile(benchmarks))
        self.save()

    ## TESTING FUNCTIONS

    def check_password_timed(self, threshold, iterations):
        """
        Returns the number of seconds it takes to check if this password is correct, with the
        given parameters.
        """
        salt = self.user.salt
        user_password = self.user.get_hashed_password(iterations)
        start = time.time()

        for p in list_permutations(self.get_permutation(), threshold=threshold):
            hashed = hash_password(self.password, salt, p, iterations=iterations)
            if constant_time_compare(hashed, user_password):
                break

        return time.time() - start

    def crack_permutation(self, threshold, iterations):
        """
        Returns the number of seconds it takes to check every permutation against
        the password, simulating an attacker that knows the password but not the
        permutation.
        """
        salt = self.user.salt
        user_password = self.user.get_hashed_password(iterations)
        start = time.time()

        for permutation in permutations(range(self.user.num_images)):
            for p in list_permutations(permutation, threshold=threshold):
                hashed = hash_password(self.password, salt, p, iterations=iterations)
                if constant_time_compare(hashed, user_password):
                    break

        return time.time() - start
