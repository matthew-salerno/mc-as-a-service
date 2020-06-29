#!/bin/bash
/bin/header.sh
cat $server_path"/logs/latest.txt"
cat $server_path"/outpipe" | sed '/.*/d'
while true; do
    cat $server_path"/outpipe"
    sleep 0.1
done
