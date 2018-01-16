#!/bin/bash

pip install virtualenv
python2 wpt run $1 --log-tbpl=- --log-wptreport=wpt_report.json --this-chunk=$3 --total-chunks=$4 --test-type=$2
