set -e

export DJANGO_SETTINGS_MODULE=flog.settings.prod

# Flush cache
echo "Flushing cache"
/opt/env/bin/python /opt/flog/manage.py flush_cache

# Aggregate websso data
echo "Aggregating SSO data"
/opt/env/bin/python /opt/flog/manage.py aggregate_events_daily 1

# Cache websso views
echo "Caching SSO auth flow, year"
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 366 1 SAML2
echo "Caching SSO auth flow, month"
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 31 1 SAML2
echo "Caching SSO auth flow, week"
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 8 1 SAML2
echo "Caching SSO auth flow, day"
/opt/env/bin/python /opt/flog/manage.py cache_auth_flow 1 1 SAML2
