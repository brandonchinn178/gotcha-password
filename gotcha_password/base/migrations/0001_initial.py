# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-11 05:21
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField()),
                ('text', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['user', 'number'],
            },
        ),
        migrations.CreateModel(
            name='LoginAttempt',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('right_password', models.BooleanField()),
                ('correct_images', models.PositiveSmallIntegerField()),
                ('raw_password', models.CharField(max_length=128)),
                ('permutation', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters and digits only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^\\w+$', 'Enter a valid username. This value may contain only letters and numbers.')])),
                ('password', models.CharField(max_length=128)),
                ('seed', models.CharField(max_length=12)),
                ('num_images', models.PositiveSmallIntegerField()),
                ('permutation', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='loginattempt',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.User'),
        ),
        migrations.AddField(
            model_name='label',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.User'),
        ),
    ]
