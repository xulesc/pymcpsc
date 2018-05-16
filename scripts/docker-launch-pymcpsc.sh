#!/bin/sh -e

xvfb-run python -u /opt/anaconda2/lib/python2.7/site-packages/pymcpsc-0.1-py2.7.egg/pymcpsc/run_pymcpsc.py "$@"


