# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import log.models


class Migration(migrations.Migration):

    dependencies = [
        ('institution', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relation_level', models.CharField(max_length=45, verbose_name='Level', choices=[(b'2', 'Second level'), (b'3', 'Third level'), (b'4', 'Fourth level')])),
                ('inst_related', models.ForeignKey(related_name='referred', verbose_name='Institution', to='institution.Institution', null=True)),
                ('institution', models.ForeignKey(related_name='related', to='institution.Institution', null=True)),
            ],
            options={
                'verbose_name': 'Relationship',
                'verbose_name_plural': 'Relationships',
            },
            bases=(models.Model, log.models.AuditLog),
        ),
        migrations.AlterField(
            model_name='contactperson',
            name='prefix',
            field=models.CharField(max_length=45, verbose_name='Prefix', choices=[(b'Mr.', 'Mr.'), (b'Mrs.', 'Mrs.'), (b'Dr.', 'Dr.')]),
        ),
    ]
