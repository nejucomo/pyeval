#!/bin/bash

set -x

TRIAL=$(which trial)

if ! [ -x "$TRIAL" ];
then
    echo 'Could not find trial; it is in the Twisted package.'
    exit -1
fi
    

PYTHONPATH="./lib:$PYTHONPATH" coverage run "$TRIAL" ./lib/pyeval
STATUS=$?

coverage html

exit $STATUS

