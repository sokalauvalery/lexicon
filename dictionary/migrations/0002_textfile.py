# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-26 15:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='')),
                ('upload_date', models.DateTimeField(verbose_name='upload date')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.Source')),
            ],
        ),
    ]
