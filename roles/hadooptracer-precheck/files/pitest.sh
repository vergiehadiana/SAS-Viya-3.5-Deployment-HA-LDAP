#!/bin/bash

JARDB="$HOME/jars.txt"
if [ ! -f $JARDB ]; then
        hadoopclasspath=`hadoop classpath`
        for i in ${hadoopclasspath//:/ }
        do
                echo "$i" 2>/dev/null >> $JARDB
                echo "$i"
        done
fi
# FIND EXAMPLES JAR FOR HADOOP 2.x or 1.x
EXAMPLEJAR=$(cat $JARDB | fgrep -v sources | egrep -v ^/tmp | fgrep -m 1 -i mapreduce-example)
if [ "$EXAMPLEJAR" == "" ]; then
    EXAMPLEJAR=$(cat $JARDB | fgrep -v sources | egrep -v ^/tmp | fgrep -m 1 -i dev-examples)
    if [ "$EXAMPLEJAR" == "" ]; then
        rm -f $JARDB
        echo "No mapreduce examples jar found"
        exit 5
    fi
fi
rm -f $JARDB
echo "EXAMPLEJAR: $EXAMPLEJAR"

# Run the job with MR1
echo "running mapreduce 1.x ..."
timeout -s SIGKILL 10m hadoop jar $EXAMPLEJAR pi 10 100
MR1RC=$?
echo "mapreduce 1.x finished: $MR1RC"

echo "checking if yarn in path ..."
YARN=`which yarn`
echo "yarn cmd count: $YARN"
which yarn
if [ $? -eq 0 ]; then

    echo "running yarn ..."
    # Run the same job with MR2
    timeout -s SIGKILL 10m yarn jar $EXAMPLEJAR pi 10 100
    MR2RC=$?
    echo "yarn finished: $MR2RC"

else
    echo "No yarn in path"
    MR2RC=0
fi

echo "Checking RCs"
if [ "$MR1RC" != "0" ] || [ "$MR2RC" != "0" ]; then
    echo "exitcodes: $MR1RC $MR2RC"
    exit 10
fi

exit $RC
