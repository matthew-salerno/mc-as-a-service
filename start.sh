#!bin/bash

config_path="$SNAP""/etc/mc-as-a-service.json"
server_path=`cat "$config_path" | jq '.launcher.server_path'` 
#load the configuration
mem_min=`cat "$config_path" | jq '.launcher.memory.min'` 
mem_max=`cat "$config_path" | jq '.launcher.memory.max'` 


#create pipe if none exists
if [ ! -f "pipe" ];
    then mkfifo pipe;
fi;
cat pipe > /dev/null

#start the server
while true;
    do temp=`cat pipe`;
    echo $temp;
    if [ "$temp" = "stop" ];
        then break;
    fi;
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar server.jar nogui;
