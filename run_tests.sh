#!/bin/bash

set -x

coverage run ./test_pyeval.py -v
STATUS=$?

coverage html

exit $STATUS

