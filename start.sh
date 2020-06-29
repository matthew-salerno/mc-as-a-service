#!/bin/bash
echo "preparing to launch server"
sleep 1
source "$SNAP"/bin/header.sh
#load the configuration
mem_min=$(cat "$config_path" | jq -r '.launcher.memory.min | @sh' | sed "s/^'//" | sed "s/'$//")
mem_max=$(cat "$config_path" | jq -r '.launcher.memory.max | @sh' | sed "s/^'//" | sed "s/'$//")
export JAVA_HOME="$SNAP""/usr/lib/jvm/java-1.8.0-openjdk-$SNAP_ARCH"
export PATH="$JAVA_HOME""/bin:$JAVA_HOME/jre/bin:$PATH"

#server won't start until input has been opened, this function is meant to be forked
function wakeup () {
    sleep 1
    echo "Opening server input"
    echo "" > "$in_pipe"
}

function cleanup () {
    echo "stop" > "$in_pipe"
    cat "" > "$out_log"
    echo "server stopped"
}

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

#clear the pipe
echo "" > "$in_pipe"

#setup ramdisk

#start the server
echo -e "Starting server at ""$jarfile_path""\nwith initial memory of ""$mem_min"" and a max memory of ""$mem_max"
wakeup &
while true; do
    temp=`cat "$in_pipe"`
    echo $temp
    #this part stops the loop when the server gets the stop command
    if [ "$temp" = "stop" ]
        then break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar "$jarfile_path" nogui >> "$out_log"

#cleanup
trap cleanup EXIT SIGINT
