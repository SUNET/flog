# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'DailyEventAggregation.total_events'
        db.delete_column(u'event_dailyeventaggregation', 'total_events')

        # Adding field 'DailyEventAggregation.num_events'
        db.add_column(u'event_dailyeventaggregation', 'num_events',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'DailyEventAggregation.total_events'
        db.add_column(u'event_dailyeventaggregation', 'total_events',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'DailyEventAggregation.num_events'
        db.delete_column(u'event_dailyeventaggregation', 'num_events')


    models = {
        u'event.dailyeventaggregation': {
            'Meta': {'unique_together': "(('date', 'origin_name', 'rp_name', 'protocol'),)", 'object_name': 'DailyEventAggregation'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'num_events': ('django.db.models.fields.BigIntegerField', [], {}),
            'origin_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'protocol': ('django.db.models.fields.SmallIntegerField', [], {}),
            'rp_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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