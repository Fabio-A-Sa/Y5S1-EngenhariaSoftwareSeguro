#!/bin/sh

set -e

cd "$(dirname "$0")/.."

./bin/create_env_files.sh
./bin/create_data_volume.sh
