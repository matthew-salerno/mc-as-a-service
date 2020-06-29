#!/bin/bash
source "$SNAP"/bin/header.sh
tail -f "$out_log" &
whi
command=`read`
while [ ! "$command" = "exit" ]; do
    echo "$command" >> $in_pipe
done
