# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('classification', '0002_collection_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='community_flag',
            field=models.BooleanField(default=False, verbose_name='Community?'),
        ),
        migrations.AddField(
            model_name='collection',
            name='type',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Collection type', choices=[(0, 'Category'), (1, 'Theme')]),
        ),
        migrations.AddField(
            model_name='collection',
            name='updated_time',
            field=models.DateTimeField(auto_now=True, verbose_name='Last update', null=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='updated_by',
            field=models.ForeignKey(related_name='+', blank=True, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='relationship',
            name='updated_time',
            field=models.DateTimeField(auto_now=True, verbose_name='updated', null=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='parent',
            field=models.ForeignKey(related_name='children', verbose_name='Parent', blank=True, to='classification.Collection', null=True),
        ),
    ]
