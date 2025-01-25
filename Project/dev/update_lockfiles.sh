#!/bin/sh

APPS=$(find "$(pwd)/apps" -mindepth 1 -maxdepth 1 -type d)

for APP in $APPS; do
    echo "Updating lockfile for app '$APP'"
    cd "$APP"
    poetry lock
done
