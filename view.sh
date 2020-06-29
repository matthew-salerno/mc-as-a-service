#!/bin/bash
source "$SNAP"/bin/header.sh

command=`read`
tail -fs 1 "$out_log"
while [ ! "$command" = "exit" ]; do
    echo "$command" > $in_pipe
    command=`read`
done
