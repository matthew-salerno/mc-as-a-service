#!/bin/bash
#Common variables used by all programs

export config_path="$SNAP_USER_DATA""/config/mc-as-a-service.json"
export server_path="$SNAP_USER_DATA""`cat "$config_path" | jq -r '.launcher.server_path | @sh' | sed "s/^'//" | sed "s/'$//"`" 
export manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"
export eula_path=$server_path"/eula.txt"
export server_jar_path="$server_path""/server.jar"
export jarfile_path="$SNAP_USER_DATA""$server_path""`cat "$config_path" | jq -r '.launcher.jarfile | @sh' | sed "s/^'//" | sed "s/'$//"`"
export $in_pipe="$server_path""/inpipe"
export $out_pipe="$server_path""/outpipe"

#make sure config exists
if [ ! -d $config_path ]; then
    mkdir $config_path
fi
#make sure server folder exists
if [ ! -d $server_path ]; then
    mkdir $server_path
fi
