#!bin/bash
config_path="$SNAP_USER_DATA""/config/mc-as-a-service.json"
server_path="$SNAP_USER_DATA""`cat "$config_path" | jq -r '.launcher.server_path | @sh' | sed "s/^'//" | sed "s/'$//"`"
echo "stop" > pipe
