#!/bin/bash

java_bin=$1
JAVA_VER=$($java_bin -XshowSettings:properties -version 2>&1 | grep -F java.version)
if (( $? != 0 ))
then
  echo $java_bin failed to execute >&2
  exit 1
elif [[ $JAVA_VER = ${JAVA_VER/= 1.8.0/} ]]
then
  echo $java_bin is not Java 8 >&2
  exit 1
elif (( ${JAVA_VER##*_} < 121 ))
then
  echo $java_bin is too old. Java must be 1.8.0_121 or greater. >&2
  exit 1
fi
