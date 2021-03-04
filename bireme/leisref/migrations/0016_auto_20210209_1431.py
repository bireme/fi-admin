# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.exceptions import ObjectDoesNotExist

from django.db import migrations, models

def forward(apps, schema_editor):
    Act = apps.get_model("leisref", "Act")
    for act in Act.objects.all():
        if act.organ_issuer_id:
            try:
                act.issuer_organ.add(act.organ_issuer)
            except ObjectDoesNotExist:
                continue

class Migration(migrations.Migration):

    dependencies = [
        ('leisref', '0015_auto_20210209_1430'),
    ]

    operations = [
        migrations.RunPython(forward)
    ]
