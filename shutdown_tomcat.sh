#!/bin/sh

PID=`netstat -ntlpu | grep tcp | grep :$1 | awk '{print $NF}' | awk -F/ '{print $1}'`
if [ $PID ];then
  $2bin/shutdown.sh
fi

PID=`netstat -ntlpu | grep tcp | grep :$1 | awk '{print $NF}' | awk -F/ '{print $1}'`
if [ $PID ];then
  kill -9 $PID
fi


