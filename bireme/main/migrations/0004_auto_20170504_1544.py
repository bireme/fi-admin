# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20160203_1435'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='abstract',
            field=models.TextField(help_text='Include information on the content and operation of the internet resource', verbose_name='Abstract'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='author',
            field=models.TextField(help_text='Enter one per line. Only filled if different from the originator of the resource', verbose_name='Authors', blank=True),
        ),
        migrations.AlterField(
            model_name='resource',
            name='originator',
            field=models.TextField(help_text='Institutional or personnel name of the responsible for the existence of the internet resource. Ex. Brazilian Society for Dental Research', verbose_name='Originator'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='title',
            field=models.CharField(help_text='Transcribe as it appears on the internet resource. If there is no title, provide a brief, simple but explanatory title', max_length=510, verbose_name='Title'),
        ),
    ]
