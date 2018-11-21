# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('thesaurus', '0002_entrycombinationlistdesc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='termlistdesc',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (3, 'Deleted'), (5, 'Historical')]),
        ),
        migrations.AlterField(
            model_name='termlistqualif',
            name='status',
            field=models.SmallIntegerField(default=-1, null=True, verbose_name='Status', choices=[(-1, 'Draft'), (1, 'Published'), (3, 'Deleted'), (5, 'Historical')]),
        ),
    ]
