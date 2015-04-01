set -e

export DJANGO_SETTINGS_MODULE=flog.settings.prod

# Flush cache
/opt/env/bin/python /opt/flog/manage.py flush_cache

# Update swedish eduroam realms
/opt/env/bin/python /opt/flog/manage.py update_realm_meta_data

# Aggregate eduroam data
/opt/env/bin/python /opt/flog/manage.py remove_duplicated_eduroam_events 1
/opt/env/bin/python /opt/flog/manage.py aggregate_eduroam_events_daily 1

# Cache eduroam views
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 366 1
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 31 1
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 8 1
/opt/env/bin/python /opt/flog/manage.py cache_eduroam_auth_flow 1 1
