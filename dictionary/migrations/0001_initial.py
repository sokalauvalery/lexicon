# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-17 19:45
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dictionary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('fibonacci', 'fibonacci'), ('power', 'power')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'pending'), ('started', 'started'), ('finished', 'finished'), ('failed', 'failed')], max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('argument', models.PositiveIntegerField()),
                ('result', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='TextFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('file', models.FileField(upload_to='')),
                ('upload_date', models.DateTimeField(verbose_name='upload date')),
                ('new_words_count', models.IntegerField(default=0)),
                ('total_words_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usage', models.TextField()),
                ('source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.Source')),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=200)),
                ('explore_date', models.DateTimeField(verbose_name='explore date')),
                ('status', models.IntegerField(choices=[(0, 'new'), (1, 'learn'), (2, 'known'), (3, 'ignore')], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Meaning',
            fields=[
                ('word', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='dictionary.Word')),
                ('meaning', models.TextField(max_length=10000)),
            ],
        ),
        migrations.AddField(
            model_name='word',
            name='source',
            field=models.ManyToManyField(to='dictionary.TextFile'),
        ),
        migrations.AddField(
            model_name='word',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usage',
            name='word',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dictionary.Word'),
        ),
    ]
