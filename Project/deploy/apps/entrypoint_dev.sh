#!/bin/sh

flask --app "${APP_NAME}:app" run --host 0.0.0.0 --port "${APP_PORT}" --debug
