#!/bin/bash
source "$SNAP"/bin/header.sh
#load the configuration
mem_min=$(cat "$config_path" | jq -r '.launcher.memory.min | @sh' | sed "s/^'//" | sed "s/'$//")
mem_max=$(cat "$config_path" | jq -r '.launcher.memory.max | @sh' | sed "s/^'//" | sed "s/'$//")
export JAVA_HOME="$SNAP""/usr/lib/jvm/java-1.8.0-openjdk-$SNAP_ARCH"
export PATH="$JAVA_HOME""/bin:$JAVA_HOME/jre/bin:$PATH"

#cd into proper directory
cd "$server_path"

#create in pipe if none exists
if [ ! -p "$in_pipe" ]
    then mkfifo "$in_pipe"
fi
#create outfile if it doesn't exist
if [ ! -f "$out.log" ]
    then echo "" > "$out_log"
fi

#deletes everything without using /dev/null
cat "$in_pipe" | sed '/.*/d'

#start the server
init="first"
while true; do
    temp=`cat "$in_pipe"`
    echo $temp
    #this mess gets the in_pipe going... somehow
    if ["$init" = "first"]; then
        init="second"
        sleep 1
    elif ["$init" = "second"]; then
        init="done"
        echo "" > "$in_pipe"
    fi
    #this part stops the loop when the server gets the stop command
    if [ "$temp" = "stop" ]
        then break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar "$jarfile_path" nogui >> "$out_log" && cat "" > "$out_log"
