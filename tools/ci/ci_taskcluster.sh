#!/bin/bash

set -xe

# To make sure we have all the deps installed
apt install firefox

pip -q install virtualenv
python2 wpt run $1 --log-tbpl=- --log-tbpl-level=debug --log-wptreport=wpt_report.json --this-chunk=$3 --total-chunks=$4 --test-type=$2 -y --install-browser
