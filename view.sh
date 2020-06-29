#!/bin/bash
source "$SNAP"/bin/header.sh

command=`read`
while [ ! "$command" = "exit" ]; do
    tail -fs "$out_log"
    echo "$command" > $in_pipe
done
