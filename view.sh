#!/bin/bash
source "$SNAP"/bin/header.sh

cleanup () {
    kill -KILL "$process"
    echo "Exited server view"
    exit 0
}

trap cleanup EXIT SIGINT

tail -f "$out_log" &
process=$!
read
while [ ! "$REPLY"="exit" ]; do
    echo "$REPLY" > "$in_pipe"
    read
done
