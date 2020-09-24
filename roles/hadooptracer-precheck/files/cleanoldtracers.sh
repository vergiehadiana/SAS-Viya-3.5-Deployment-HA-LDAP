#!/bin/bash

PIDS=$(ps aux | fgrep -i -e "hadooptracer.py" -e "strace" | fgrep -v grep | awk '{print $2}')

for PID in $PIDS; do
    ps aux | fgrep -i " $PID "
    timeout -s SIGKILL 10s kill -9 $PID
done
