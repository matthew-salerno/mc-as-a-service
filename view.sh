#!/bin/bash
source "$SNAP"/bin/header.sh

cleanup () {
    kill -KILL "$process"
    echo "Exited server view"
    exit 0
}

no_ctrl_c () {
    echo -e "Type \"exit\" to leave"
}


trap cleanup EXIT
trap no_ctrl_c SIGINT

tail -f "$out_log" &
process=$!
read
while [ ! "$REPLY" == "exit" ]; do
    echo "$REPLY" > "$in_pipe"
    if [ "$REPLY" == "stop" ]; then
        break
    fi
    read
done
