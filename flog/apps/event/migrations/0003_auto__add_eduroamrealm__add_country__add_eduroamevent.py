# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EduroamRealm'
        db.create_table(u'event_eduroamrealm', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('realm', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=256, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='country_realms', null=True, on_delete=models.SET_NULL, to=orm['event.Country'])),
        ))
        db.send_create_signal(u'event', ['EduroamRealm'])

        # Adding model 'Country'
        db.create_table(u'event_country', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=3)),
            ('name', self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=256, blank=True)),
        ))
        db.send_create_signal(u'event', ['Country'])

        # Adding model 'EduroamEvent'
        db.create_table(u'event_eduroamevent', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('realm', self.gf('django.db.models.fields.related.ForeignKey')(related_name='realm_events', to=orm['event.EduroamRealm'])),
            ('visited_country', self.gf('django.db.models.fields.related.ForeignKey')(related_name='country_events', to=orm['event.Country'])),
            ('visited_institution', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='institution_events', null=True, on_delete=models.SET_NULL, to=orm['event.EduroamRealm'])),
            ('calling_station_id', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('successful', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'event', ['EduroamEvent'])


    def backwards(self, orm):
        # Deleting model 'EduroamRealm'
        db.delete_table(u'event_eduroamrealm')

        # Deleting model 'Country'
        db.delete_table(u'event_country')

        # Deleting model 'EduroamEvent'
        db.delete_table(u'event_eduroamevent')


    models = {
        u'event.country': {
            'Meta': {'ordering': "['country_code']", 'object_name': 'Country'},
            'country_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '256', 'blank': 'True'})
        },
        u'event.eduroamevent': {
            'Meta': {'object_name': 'EduroamEvent'},
            'calling_station_id': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'realm': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'realm_events'", 'to': u"orm['event.EduroamRealm']"}),
            'successful': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'visited_country': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'country_events'", 'to': u"orm['event.Country']"}),
            'visited_institution': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'institution_events'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['event.EduroamRealm']"})
        },
        u'event.eduroamrealm': {
            'Meta': {'ordering': "['realm']", 'object_name': 'EduroamRealm'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'country_realms'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['event.Country']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256', 'blank': 'True'}),
            'realm': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'})
        },
        u'event.entity': {
            'Meta': {'ordering': "['uri']", 'object_name': 'Entity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_idp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_rp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uri': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        },
        u'event.event': {
            'Meta': {'object_name': 'Event'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origin_events'", 'to': u"orm['event.Entity']"}),
            'principal': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'protocol': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rp_events'", 'to': u"orm['event.Entity']"}),
            'ts': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        }
    }

    complete_apps = ['event']