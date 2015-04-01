set -e

export DJANGO_SETTINGS_MODULE=flog.settings.prod

# Flush cache
/opt/env/bin/python /opt/flog/manage.py flush_cache

# Aggregate websso data
/opt/env/bin/python /opt/flog/manage.py aggregate_events_daily 1

# Cache websso views
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 366 1 SAML2
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 31 1 SAML2
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 8 1 SAML2
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 1 1 SAML2
