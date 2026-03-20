# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_event_not_regional_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='address',
            field=models.CharField(help_text='Enter full address of the local of the event to present it in a Google map', max_length=255, verbose_name='Address', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='link',
            field=models.URLField(help_text='Enter the link of event portal', max_length=255, verbose_name='Link', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='observations',
            field=models.TextField(help_text='Enter information about institutions that organize and/or sponsor the event, deadline for submission of papers, simultaneous translation service, event program, etc.', verbose_name='Observations', blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='title',
            field=models.CharField(help_text='Enter the full name of the event, as it appears and in the same language. Ex: XIX Congresso Brasileiro de Arritmias Cardiacas. XVII Simposio Nacional do DECS-SBCC', max_length=455, verbose_name='Title'),
        ),
    ]
