# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0008_auto_20191029_1758'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contactemail',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='contactperson',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='contactphone',
            name='institution',
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='type',
            options={'verbose_name': 'Type', 'verbose_name_plural': 'Types'},
        ),
        migrations.AlterField(
            model_name='adm',
            name='category_history',
            field=models.TextField(verbose_name='Category (history)', blank=True),
        ),
        migrations.AlterField(
            model_name='adm',
            name='type_history',
            field=models.TextField(verbose_name='Type (history)', blank=True),
        ),
        migrations.DeleteModel(
            name='ContactEmail',
        ),
        migrations.DeleteModel(
            name='ContactPerson',
        ),
        migrations.DeleteModel(
            name='ContactPhone',
        ),
    ]
