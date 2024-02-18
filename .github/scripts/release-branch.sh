#!/bin/sh
set -e

#
# entry script to create a release branch in ci
# generates a release branch named with a utc timestamp
#
echo 'CREATING A RELEASE BRANCH'

# create a release branch locally and remotely
# normalize utc date to YYYY-MM-DD-HH-MM
NEW_BRANCH_NAME="release/$(date -u +%Y-%m-%d-%H-%M)"
echo "NEW BRANCH: $NEW_BRANCH_NAME"
git checkout -b $NEW_BRANCH_NAME
git push origin $NEW_BRANCH_NAME