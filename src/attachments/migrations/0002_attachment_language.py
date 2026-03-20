# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='language',
            field=models.CharField(default='pt', max_length=10, verbose_name='Language', choices=[(b'en', 'English'), (b'pt-br', 'Portuguese'), (b'es', 'Spanish')]),
            preserve_default=False,
        ),
    ]
