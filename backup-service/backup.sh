#!/usr/bin/env bash

set -e

container_name="nexus_server_container"
data_path="/app/src/data"
backup_dir="/home/nexus/nexus_server/"
located_data="/home/nexus/nexus_server/data"

rm -rf $located_data
docker cp $container_name:$data_path $backup_dir