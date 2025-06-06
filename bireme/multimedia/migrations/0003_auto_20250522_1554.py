# Generated by Django 2.2.24 on 2025-05-22 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0008_auto_20250522_1554'),
        ('multimedia', '0002_auto_20170308_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='publication_country',
            field=models.ManyToManyField(blank=True, to='utils.Country', verbose_name='Publication country'),
        ),
        migrations.AlterField(
            model_name='media',
            name='publication_date',
            field=models.DateField(blank=True, help_text='Format: DD/MM/YYYY', null=True, verbose_name='Publication date'),
        ),
        migrations.AlterField(
            model_name='mediacollection',
            name='date',
            field=models.DateField(blank=True, help_text='Format: DD/MM/YYYY', null=True, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='mediacollection',
            name='language',
            field=models.CharField(blank=True, choices=[('en', 'English'), ('pt-br', 'Portuguese'), ('es', 'Spanish'), ('fr', 'French')], max_length=10, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='mediacollectionlocal',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('pt-br', 'Portuguese'), ('es', 'Spanish'), ('fr', 'French')], max_length=10, verbose_name='language'),
        ),
        migrations.AlterField(
            model_name='mediatype',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('pt-br', 'Portuguese'), ('es', 'Spanish'), ('fr', 'French')], max_length=10, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='mediatypelocal',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('pt-br', 'Portuguese'), ('es', 'Spanish'), ('fr', 'French')], max_length=10, verbose_name='language'),
        ),
    ]
