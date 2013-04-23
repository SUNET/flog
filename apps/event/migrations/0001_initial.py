# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Entity'
        db.create_table(u'event_entity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uri', self.gf('django.db.models.fields.URLField')(unique=True, max_length=200)),
            ('is_idp', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_rp', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'event', ['Entity'])

        # Adding model 'Event'
        db.create_table(u'event_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('ts', self.gf('django.db.models.fields.DateTimeField')()),
            ('origin', self.gf('django.db.models.fields.related.ForeignKey')(related_name='origin_events', to=orm['event.Entity'])),
            ('rp', self.gf('django.db.models.fields.related.ForeignKey')(related_name='rp_events', to=orm['event.Entity'])),
            ('protocol', self.gf('django.db.models.fields.SmallIntegerField')()),
            ('principal', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'event', ['Event'])


    def backwards(self, orm):
        # Deleting model 'Entity'
        db.delete_table(u'event_entity')

        # Deleting model 'Event'
        db.delete_table(u'event_event')


    models = {
        u'event.entity': {
            'Meta': {'ordering': "['uri']", 'object_name': 'Entity'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_idp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_rp': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'uri': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200'})
        },
        u'event.event': {
            'Meta': {'object_name': 'Event'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'origin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'origin_events'", 'to': u"orm['event.Entity']"}),
            'principal': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'protocol': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rp': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'rp_events'", 'to': u"orm['event.Entity']"}),
            'ts': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['event']