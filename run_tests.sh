#!/bin/bash

PYTHONPATH="./lib:$PYTHONPATH"


echo '=== pyflakes ==='
pyflakes ./lib/pyeval || exit $?


echo '=== Running unittests ==='
TRIAL=$(which trial)

if ! [ -x "$TRIAL" ];
then
    echo 'Could not find trial; it is in the Twisted package.'
    exit -1
fi


coverage run "$TRIAL" ./lib/pyeval
STATUS=$?

echo '--- Generating Coverage Report ---'
coverage html --include='lib/pyeval/*'

[ "$STATUS" -eq 0 ] || exit $STATUS


echo '=== Smoke Test ==='
exec ./bin/pyeval 'os._exit(0)'

