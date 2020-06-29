#!/bin/bash
source "$SNAP"/bin/header.sh

command=`read`
while [ ! "$command" = "exit" ]; do
    tail -fs "0.5" "$out_log"
    echo "$command" > $in_pipe
done
