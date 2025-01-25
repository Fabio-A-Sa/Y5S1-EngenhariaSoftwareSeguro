#!/bin/sh

USER_ID="$1"
GROUP_ID="$2"

GROUP=$(getent group "$GROUP_ID" | cut -d: -f1)
if [ -z "$GROUP" ]; then
    addgroup -g "$GROUP_ID" app
    GROUP="app"
fi

USER=$(getent passwd "$USER_ID" | cut -d: -f1)
if [ -z "$USER" ]; then
    adduser -u "$USER_ID" -G "$GROUP" -s /bin/sh -D app
    USER="app"
else
    adduser "$USER" "$GROUP"
fi

echo $USER
