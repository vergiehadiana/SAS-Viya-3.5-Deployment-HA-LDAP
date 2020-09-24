#!/bin/bash 
RC=0

timeout -s SIGKILL 30s hadoop job -list
TRC=$?
if [ "$TRC" != "0" ]; then
    exit $TRC
fi

JOBS=$(timeout -s SIGKILL 30s hadoop job -list | awk '{print $1}' | egrep ^job_) 

for JOB in $JOBS; do
    echo $JOB
    timeout -s SIGKILL 10s $(which hadoop) job -kill $JOB
    TRC=$?
    echo "## MRKILLER: $JOB --> $TRC"
    if [ "$TRC" != "0" ]; then
        RC=$TRC
    fi
done
exit $RC
