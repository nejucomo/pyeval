#!/bin/bash

PYTHONPATH=".:$PYTHONPATH"


echo '=== pyflakes ==='
pyflakes ./pyeval || exit $?
echo 'pyflakes completed.'


echo -e '\n=== Running unittests ==='
TRIAL=$(which trial)

if ! [ -x "$TRIAL" ];
then
    echo 'Could not find trial; it is in the Twisted package.'
    exit -1
fi


coverage run --branch "$TRIAL" ./pyeval
STATUS=$?

echo -e '\n--- Generating Coverage Report ---'
coverage html --include='pyeval/*'

echo 'Report generated.'

[ "$STATUS" -eq 0 ] || exit $STATUS


echo -e '\n=== Smoke Test ==='
./bin/pyeval 'os._exit(0)'
STATUS=$?

if [ "$STATUS" -eq 0 ]
then
    echo 'Smoke-test Succeeded.'
else
    echo 'Smoke-test FAILED.'
fi

exit "$STATUS"
