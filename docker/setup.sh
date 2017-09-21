#!/bin/bash
#
# Install all requirements
#

set -e
set -x

apt-get update
apt-get -y dist-upgrade
apt-get -y install \
    build-essential \
    python-dev \
    python-virtualenv \
    libpq-dev
apt-get clean
rm -rf /var/lib/apt/lists/*

# Create virtualenv
virtualenv /opt/env
