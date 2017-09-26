set -e

export DJANGO_SETTINGS_MODULE=flog.settings.prod

# Flush cache
echo "Flushing cache"
/opt/env/bin/python /opt/flog/manage.py flush_cache

# Update swedish eduroam realms
echo "Updating realm data"
/opt/env/bin/python /opt/flog/manage.py update_realm_meta_data

# Aggregate eduroam data
#echo "Removing duplicate eduroam F-TICKs"
#/opt/env/bin/python /opt/flog/manage.py remove_duplicated_eduroam_events 1
echo "Aggregating eduroam data"
/opt/env/bin/python /opt/flog/manage.py aggregate_eduroam_events_daily 1

# Cache eduroam views
echo "Caching eduroam auth flow, year"
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 366 1
echo "Caching eduroam auth flow, month"
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 31 1
echo "Caching eduroam auth flow, week"
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 8 1
echo "Caching eduroam auth flow, day"
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 1 1
