#!/bin/sh

set -e
set -x

. /opt/env/bin/activate

# These could be set from Puppet if multiple instances are deployed
app_name=${app_name-"flog"}
base_dir=${base_dir-"/opt/flog"}
project_dir=${project_dir-"${base_dir}/flog"}
# These *can* be set from Puppet, but are less expected to...
log_dir=${log_dir-'/opt/flog/logs'}
state_dir=${state_dir-"${base_dir}/run"}
workers=${workers-1}
worker_class=${worker_class-"sync"}
worker_threads=${worker_threads-1}
worker_timeout=${worker_timeout-30}

mkdir -p ${state_dir} ${log_dir}

# set PYTHONPATH if it is not already set using Docker environment
export PYTHONPATH=${PYTHONPATH-${project_dir}}

# set Django settings module
export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE-"flog.settings.prod"}

extra_args=""
if [ -f "/opt/src/flog/manage.py" ]; then
    # developer mode, restart on code changes
    extra_args="--reload"
fi

# nice to have in docker run output, to check what
# version of something is actually running.
/opt/env/bin/pip freeze

# Collect static files
/opt/env/bin/python /opt/flog/manage.py collectstatic --noinput

echo "Starting flog app"
exec start-stop-daemon --chdir ${base_dir} \
     --start --exec \
     /opt/env/bin/gunicorn \
     --pidfile "${state_dir}/${app_name}.pid" \
     -- \
     --bind 0.0.0.0:8000 \
     --workers ${workers} --worker-class ${worker_class} \
     --threads ${worker_threads} --timeout ${worker_timeout} \
     --access-logfile "${log_dir}/${app_name}-access.log" \
     --error-logfile "${log_dir}/${app_name}-error.log" \
     --capture-output \
     ${extra_args} flog.wsgi

