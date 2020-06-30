#!/bin/bash
echo "preparing to launch server"
sleep 1
source "$SNAP"/bin/header.sh
#load the configuration
mem_min=$(cat "$config_path" | jq -r '.launcher.memory.min | @sh' | sed "s/^'//" | sed "s/'$//")
mem_max=$(cat "$config_path" | jq -r '.launcher.memory.max | @sh' | sed "s/^'//" | sed "s/'$//")
export JAVA_HOME="$SNAP""/usr/lib/jvm/java-1.8.0-openjdk-$SNAP_ARCH"
export PATH="$JAVA_HOME""/bin:$JAVA_HOME/jre/bin:$PATH"


shutdown () {
    kill -KILL $spinny_pid
    echo "stop" > "$in_pipe"
    echo "`jobs -p $server_pid`"
    if [ ! "`pgrep -a java | grep "$server_pid"`" == "" ]; then
        echo "waiting for server with PID ""$server_pid"" to shut down"
        spinny &
        spin_pid=$!
        while [ ! "`pgrep -a java | grep "$server_pid"`" == "" ]; do
            sleep 1
        done
        kill -KILL $spin_pid
        
        echo "server shut down"
    else
        echo "server is not running"
    fi
    cleanup
    }

cleanup () {
    echo "cleaning up"
    echo "" > "$out_log"
    echo "cleaned up"
    exit 0
}

interrupted () {
    echo "Server interupted, shutting down"
    shutdown
}

trap shutdown SIGINT

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
#setup ramdisk
#start the server
echo -e "Starting server at ""$jarfile_path""\nwith initial memory of ""$mem_min"" and a max memory of ""$mem_max"
while true; do
    temp=`cat "$in_pipe"`
    echo $temp
    #this part stops the loop when the server gets the stop command
    if [ "$temp" == "stop" ]
        then break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar "$jarfile_path" nogui >> "$out_log" &
server_pid=$!
echo "Server is running with PID of ""$server_pid"
spinny &
spinny_pid=$!
while [ ! "`pgrep -a java | grep "$server_pid"`" == "" ]; do
            sleep 5
done
shutdown
