# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0005_auto_20181105_1053'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entrycombinationlistdesc',
            old_name='ecout_id',
            new_name='ecout_desc_id',
        ),
        migrations.AddField(
            model_name='entrycombinationlistdesc',
            name='ecout_qualif',
            field=models.CharField(max_length=250, verbose_name='Qualifier string', blank=True),
        ),
        migrations.AddField(
            model_name='entrycombinationlistdesc',
            name='ecout_qualif_id',
            field=models.CharField(max_length=250, verbose_name='Identifier', blank=True),
        ),
    ]
