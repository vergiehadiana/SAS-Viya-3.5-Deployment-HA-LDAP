#!/bin/bash

RC=0
HDFS=$(which hdfs 2>/dev/null)
echo $HDFS
if [ "$HDFS" != "" ]; then

    MODE=$(hdfs dfsadmin -safemode get | awk '{print $NF}' | tr '[:lower:]' '[:upper:]')
    echo "SAFEMODE: $MODE"
    if [ "$MODE" == "ON" ]; then
        hdfs dfsadmin -safemode leave
        RC=$?
    fi
else
    echo "no hdfs command"
fi
exit $RC

