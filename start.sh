#!/bin/bash
echo "preparing to launch server"
sleep 1
source "$SNAP"/bin/header.sh

if [ -f "$server_path"/server.properties ]; then
    world_path=""$server_path"/`cat "$server_path"/server.properties | sed -n 's/level-name=//p'`"
else
    world_path=$(cat "$server_path"/world)
fi

start_ramdisk () {
    mkdir "$ramdisk_path"
    if [ $ramdisk_ramfs == "false" ]; then
        mount -t tmpfs -o "$ramdisk_size" mc-ramdisk "$ramdisk_path"
    else
        mount -t ramfs -o "$ramdisk_size" mc-ramdisk "$ramdisk_path"
    fi
}

backup_ramdisk_cycle () {
    while true; do
        backup_ramdisk
        sleep "$ramdisk_interval"
    done
}

backup_ramdisk () {
    echo "say Server is backing up ramdisk" > "$in_pipe"
    rsync -ra "$ramdisk_path" "$world_path"
    echo "say Server is done backing up ramdisk" > "$in_pipe"
}

stop_ramdisk () {
    umount
}

stop_server () {
    kill -KILL $spinny_pid
    
    if [ ! "`pgrep -a java | grep "$server_pid"`" == "" ]; then
        echo "stop" > "$in_pipe"
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
    stop_server
}

trap interrupted SIGINT

#cd into proper directory
cd "$server_path"


#create in pipe if none exists
if [ ! -p "$in_pipe" ]; then
    mkfifo "$in_pipe"
fi
#create outfile if it doesn't exist
if [ ! -f "$out.log" ]; then
    echo "" > "$out_log"
fi
#setup ramdisk
#start the server
echo -e "Starting server at ""$jarfile_path""\nwith initial memory of ""$mem_min"" and a max memory of ""$mem_max"
while true; do
    temp=`cat "$in_pipe"`
    echo $temp
    #this part stops the loop when the server gets the stop command
    if [ "$temp" == "stop" ]; then
        break
    fi
done | java -Xmx"$mem_max" -Xms"$mem_min" -jar "$jarfile_path" nogui >> "$out_log" &
server_pid=$!
echo "Server is running with PID of ""$server_pid"
spinny &
spinny_pid=$!
while [ ! "`pgrep -a java | grep "$server_pid"`" == "" ]; do
            sleep 5
done
stop_server
