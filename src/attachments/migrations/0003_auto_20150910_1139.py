# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import attachments.models


class Migration(migrations.Migration):

    dependencies = [
        ('attachments', '0002_attachment_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='short_url',
            field=models.CharField(default='default', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='attachment',
            name='attachment_file',
            field=models.FileField(upload_to=attachments.models.attachment_upload, verbose_name='Select a file', blank=True),
            preserve_default=True,
        ),
    ]
