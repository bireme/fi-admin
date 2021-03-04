# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0014_actrelationship_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='act',
            name='issuer_organ',
            field=models.ManyToManyField(to='leisref.ActOrganIssuer', verbose_name='Organ issuer', blank=True),
        ),
        migrations.AlterField(
            model_name='act',
            name='organ_issuer',
            field=models.ForeignKey(related_name='old_organ_issuer', verbose_name='Organ issuer', blank=True, to='leisref.ActOrganIssuer', null=True),
        ),
    ]
