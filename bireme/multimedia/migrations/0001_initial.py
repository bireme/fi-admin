# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'MediaType'
        db.create_table(u'multimedia_mediatype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('acronym', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'multimedia', ['MediaType'])

        # Adding model 'MediaTypeLocal'
        db.create_table(u'multimedia_mediatypelocal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multimedia.MediaType'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'multimedia', ['MediaTypeLocal'])

        # Adding model 'MediaCollection'
        db.create_table(u'multimedia_mediacollection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('cooperative_center_code', self.gf('django.db.models.fields.CharField')(max_length=55, blank=True)),
        ))
        db.send_create_signal(u'multimedia', ['MediaCollection'])

        # Adding model 'MediaCollectionLocal'
        db.create_table(u'multimedia_mediacollectionlocal', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('media_collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multimedia.MediaCollection'])),
            ('language', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'multimedia', ['MediaCollectionLocal'])

        # Adding model 'Media'
        db.create_table(u'multimedia_media', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('updated_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['auth.User'])),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=0, null=True)),
            ('media_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multimedia.MediaType'])),
            ('media_collection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multimedia.MediaCollection'], null=True, blank=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=455)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('authors', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('contributors', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('dimension', self.gf('django.db.models.fields.CharField')(max_length=155, blank=True)),
            ('duration', self.gf('django.db.models.fields.CharField')(max_length=155, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=155, blank=True)),
            ('cooperative_center_code', self.gf('django.db.models.fields.CharField')(max_length=55, blank=True)),
        ))
        db.send_create_signal(u'multimedia', ['Media'])

        # Adding M2M table for field language on 'Media'
        m2m_table_name = db.shorten_name(u'multimedia_media_language')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('media', models.ForeignKey(orm[u'multimedia.media'], null=False)),
            ('sourcelanguage', models.ForeignKey(orm[u'main.sourcelanguage'], null=False))
        ))
        db.create_unique(m2m_table_name, ['media_id', 'sourcelanguage_id'])


    def backwards(self, orm):
        # Deleting model 'MediaType'
        db.delete_table(u'multimedia_mediatype')

        # Deleting model 'MediaTypeLocal'
        db.delete_table(u'multimedia_mediatypelocal')

        # Deleting model 'MediaCollection'
        db.delete_table(u'multimedia_mediacollection')

        # Deleting model 'MediaCollectionLocal'
        db.delete_table(u'multimedia_mediacollectionlocal')

        # Deleting model 'Media'
        db.delete_table(u'multimedia_media')

        # Removing M2M table for field language on 'Media'
        db.delete_table(db.shorten_name(u'multimedia_media_language'))


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'main.sourcelanguage': {
            'Meta': {'object_name': 'SourceLanguage'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'multimedia.media': {
            'Meta': {'object_name': 'Media'},
            'authors': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'contributors': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cooperative_center_code': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'dimension': ('django.db.models.fields.CharField', [], {'max_length': '155', 'blank': 'True'}),
            'duration': ('django.db.models.fields.CharField', [], {'max_length': '155', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['main.SourceLanguage']", 'symmetrical': 'False', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '155', 'blank': 'True'}),
            'media_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.MediaCollection']", 'null': 'True', 'blank': 'True'}),
            'media_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.MediaType']"}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'null': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '455'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        u'multimedia.mediacollection': {
            'Meta': {'object_name': 'MediaCollection'},
            'cooperative_center_code': ('django.db.models.fields.CharField', [], {'max_length': '55', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'multimedia.mediacollectionlocal': {
            'Meta': {'object_name': 'MediaCollectionLocal'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'media_collection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.MediaCollection']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'multimedia.mediatype': {
            'Meta': {'object_name': 'MediaType'},
            'acronym': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'created_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'updated_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'multimedia.mediatypelocal': {
            'Meta': {'object_name': 'MediaTypeLocal'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'media_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['multimedia.MediaType']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['multimedia']