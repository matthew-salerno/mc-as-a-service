#!/bin/bash
source "$SNAP"/bin/header.sh
#load the configuration
mem_min=$(cat "$config_path" | jq -r '.launcher.memory.min | @sh' | sed "s/^'//" | sed "s/'$//")
mem_max=$(cat "$config_path" | jq -r '.launcher.memory.max | @sh' | sed "s/^'//" | sed "s/'$//")
export JAVA_HOME="$SNAP""/usr/lib/jvm/java-1.8.0-openjdk-$SNAP_ARCH"
export PATH="$JAVA_HOME""/bin:$JAVA_HOME/jre/bin:$PATH"

#cd into proper directory
cd "$server_path"

#create pipes if none exists
if [ ! -f "$in_pipe" ]
    then mkfifo "$in_pipe"
fi
if [ ! -f "$out_pipe" ]
    then mkfifo "$out_pipe"
fi

#deletes everything without using /dev/null
cat "$in_pipe" | sed '/.*/d'

#start the server
while true; do
    temp=`cat "$in_pipe"`
    echo $temp
    if [ "$temp" = "stop" ]
        then break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar server.jar nogui >> "$out_pipe"
