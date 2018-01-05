#!/bin/bash

set -efuo pipefail

VIRTUALENV="$(which virtualenv)"

if ! [ -x "$VIRTUALENV" ];
then
    echo 'pyeval run_tests.sh requires virtualenv.'
    exit 1
fi

VENVDIR="${TMPDIR:-/tmp}/${USER}-pyeval-venv"

echo "=== Initializing virtualenv $VENVDIR ==="
if ! [ -d "$VENVDIR" ]
then
    eval "$VIRTUALENV" "$VENVDIR"
fi

PATH="${VENVDIR}/bin:$PATH"

pip install pyflakes
pip install coverage
pip install Twisted
pip uninstall -y pyeval || true
pip install .


echo -e '\n=== pyflakes ==='
pyflakes ./pyeval
echo 'pyflakes completed.'


echo -e '\n=== Running unittests ==='
TRIAL="$(which trial)"

set +e
coverage run --branch "$TRIAL" pyeval
STATUS=$?
set -e

echo -e '\n--- Generating Coverage Report ---'
# This is a bit circular, thus brittle. We're using the test target pyeval:
COVINC="$(pyeval 'sh(os.path.dirname(ai.path(pyeval)))')"
coverage html --include="${COVINC}/*"

echo 'Report generated.'

[ "$STATUS" -eq 0 ] || exit $STATUS


echo -e '\n=== Smoke Test ==='
set +e
python -c 'import pyeval.main; pyeval.main.main()' 'os._exit(23)'
STATUS=$?
set -e

if [ "$STATUS" -eq 23 ]
then
    echo 'Smoke-test Succeeded.'
else
    echo 'Smoke-test FAILED.'
fi

exit "$STATUS"
