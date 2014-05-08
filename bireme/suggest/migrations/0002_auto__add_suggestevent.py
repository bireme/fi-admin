# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SuggestEvent'
        db.create_table(u'suggest_suggestevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=455)),
            ('start_date', self.gf('django.db.models.fields.DateField')()),
            ('end_date', self.gf('django.db.models.fields.DateField')()),
            ('link', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=125, blank=True)),
            ('administrative_comments', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'suggest', ['SuggestEvent'])


    def backwards(self, orm):
        # Deleting model 'SuggestEvent'
        db.delete_table(u'suggest_suggestevent')


    models = {
        u'suggest.suggestevent': {
            'Meta': {'object_name': 'SuggestEvent'},
            'administrative_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '125', 'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '455'})
        },
        u'suggest.suggestresource': {
            'Meta': {'object_name': 'SuggestResource'},
            'abstract': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'administrative_comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['suggest']