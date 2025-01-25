#!/bin/sh

set -e

USER_ID="$(stat -c %u .)"
GROUP_ID="$(stat -c %g .)"

USER="$(./deploy/scripts/bin/create_user.sh "$USER_ID" "$GROUP_ID")"
su "$USER" -c "$@"
