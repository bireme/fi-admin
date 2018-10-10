# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.validators


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0011_auto_20180412_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='act',
            name='cooperative_center_code',
            field=models.CharField(max_length=55, verbose_name='Cooperative center', blank=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='issue_date',
            field=models.DateField(blank=True, help_text=b'DD/MM/YYYY', null=True, verbose_name='Issue date', validators=[utils.validators.valid_min_year]),
        ),
        migrations.AlterField(
            model_name='act',
            name='publication_date',
            field=models.DateField(blank=True, help_text=b'DD/MM/YYYY', null=True, verbose_name='Publication date', validators=[utils.validators.valid_min_year]),
        ),
    ]
