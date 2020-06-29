#!/bin/bash
source "$SNAP"/bin/header.sh
tail -f "$out_log" &
cat 0 >> "$in_pipe"
