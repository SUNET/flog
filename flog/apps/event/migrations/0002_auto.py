# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Event', fields ['ts']
        db.create_index(u'event_event', ['ts'])

        # Adding index on 'Entity', fields ['uri']
        db.create_index(u'event_entity', ['uri'])


    def backwards(self, orm):
        # Removing index on 'Entity', fields ['uri']
        db.delete_index(u'event_entity', ['uri'])

        # Removing index on 'Event', fields ['ts']
        db.delete_index(u'event_event', ['ts'])


    models = {
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