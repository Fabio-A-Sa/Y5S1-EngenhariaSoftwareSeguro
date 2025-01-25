#!/bin/sh

set -e

cd "$(dirname "$0")/.."

# Copy .env.example to .env if .env doesn't exist
for file in $(find apps -type f -name .env.example); do
    if [ ! -f "$(dirname "$file")/.env" ]; then
        cp "$file" "$(dirname "$file")/.env"
    fi
done