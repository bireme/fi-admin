# Generated by Django 2.2.24 on 2023-06-27 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20230626_2029'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_modality',
            field=models.CharField(blank=True, choices=[('in-person', 'In-person'), ('hybrid', 'Hybrid'), ('online', 'Online')], max_length=55, verbose_name='Event modality'),
        ),
    ]
