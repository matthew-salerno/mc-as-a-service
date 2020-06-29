#!/bin/bash
source "$SNAP"/bin/header.sh

function cleanup () {
    kill "$process"
}

tail -f "$out_log" &
process=&!
read
while [ ! "$REPLY"="exit" ]; do
    echo "$REPLY" > "$in_pipe"
    read
done
trap cleanup EXIT
