#!/bin/bash
#Common variables used by all programs

config_path="$SNAP_COMMON""/config/mc-as-a-service.json"


spinny() {
    local i sp n
    sp='/-\|'
    n=${#sp}
    printf ' '
    while sleep 0.1; do
        printf "%s\b" "${sp:i++%n:1}"
    done
}

#make sure config directory exists
if [ ! -d "$SNAP_COMMON""/config" ]; then
    mkdir "$SNAP_COMMON""/config"
fi
#make sure config exists
if [ ! -f $config_path ]; then
    cp "$SNAP""/etc/default-config.json" "$config_path"
fi

export server_path="$SNAP_COMMON""`cat "$config_path" | jq -r '.launcher.server_path | @sh' | sed "s/^'//" | sed "s/'$//"`" 

#make sure server folder exists
if [ ! -d $server_path ]; then
    mkdir $server_path
fi

jarfile_path="$server_path""/""`cat "$config_path" | jq -r '.launcher.jarfile | @sh' | sed "s/^'//" | sed "s/'$//"`"
eula_path="$server_path""/eula.txt"
server_jar_path="$server_path""/server.jar"
manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"
in_pipe="$server_path""/inpipe"
out_log="$server_path""/out.log"
mem_min=$(cat "$config_path" | jq -r '.launcher.memory.min | @sh' | sed "s/^'//" | sed "s/'$//")
mem_max=$(cat "$config_path" | jq -r '.launcher.memory.max | @sh' | sed "s/^'//" | sed "s/'$//")
ramdisk_path=$(cat "$config_path" | jq -r '.launcher.ramdisk.file | @sh' | sed "s/^'//" | sed "s/'$//")
ramdisk_enabled=$(cat "$config_path" | jq -r '.launcher.ramdisk.enabled | @sh' | sed "s/^'//" | sed "s/'$//")
ramdisk_size=$(cat "$config_path" | jq -r '.launcher.ramdisk.size | @sh' | sed "s/^'//" | sed "s/'$//")
ramdisk_ramfs=$(cat "$config_path" | jq -r '.launcher.ramdisk.can_outgrow_size | @sh' | sed "s/^'//" | sed "s/'$//")
ramdisk_interval=$(cat "$config_path" | jq -r '.launcher.ramdisk.interval | @sh' | sed "s/^'//" | sed "s/'$//")
let "ramdisk_interval*=60"
export JAVA_HOME="$SNAP""/usr/lib/jvm/java-1.8.0-openjdk-$SNAP_ARCH"
export PATH="$JAVA_HOME""/bin:$JAVA_HOME/jre/bin:$PATH"
