#!/bin/bash
#
# Run build commands that should never be docker-build cached
#

set -e
set -x

cd /opt/flog/

PYPI="https://pypi.sunet.se/simple/"
/opt/env/bin/pip install -i ${PYPI} -r requirements/prod.txt

/opt/env/bin/pip freeze
