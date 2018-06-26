#!/bin/sh -e

#
# This script is a convenience wrapper to enable a user to launch
# pymcpsc in a docker image. The primary reason for this script
# to exist is the need to launch pymcpsc with x-server support
# due to the Qt dependency. If at a future date this dependency
# is deprecated this script will in all likelihood become
# redundant.
#
# The path to the run script of pymcpsc is explicitly coded into
# this script. Any parameters passed to this script and forwarded
# without alteration to the pymcpsc run script
#

ANACONDA_PATH="/opt/anaconda2/"
PYMCPSC_PATH="$ANACONDA_PATH/lib/python2.7/site-packages/pymcpsc-0.1-py2.7.egg/pymcpsc"

trap 'case $? in
        139) echo "NOTE: This segfault is a known issue of the xvfb program and unrelated to pymcpsc execution";;
      esac' EXIT
xvfb-run python -u $PYMCPSC_PATH/run_pymcpsc.py "$@"



