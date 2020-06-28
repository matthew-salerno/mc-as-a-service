#!/bin/bash

config_path="$SNAP""/etc/mc-as-a-service.json"
server_path="$SNAP""`cat "$config_path" | jq -r '.launcher.server_path | @sh' | sed "s/^'//" | sed "s/'$//"`"
#load the configuration
mem_min=`cat "$config_path" | jq '.launcher.memory.min'` 
mem_max=`cat "$config_path" | jq '.launcher.memory.max'` 

#create pipes if none exists
if [ ! -f "inpipe" ]
    then mkfifo "$server_path""/inpipe"
fi
if [ ! -f "outpipe" ]
    then mkfifo "$server_path""/outpipe"
fi

#deletes everything without using /dev/null
cat pipe | sed '/.*/d'

#start the server
while true; do
    temp=`cat "$server_path""/inpipe"`
    echo $temp
    if [ "$temp" = "stop" ]
        then break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar server.jar nogui >> "$server_path""/outpipe"
