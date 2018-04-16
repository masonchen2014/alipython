#!/bin/sh

PID=`netstat -ntlpu | grep tcp | grep :48009 | awk '{print $NF}' | awk -F/ '{print $1}'`
if [ $PID ];then
  /home/chenmusheng/apache-tomcat-8.5.6/bin/shutdown.sh
fi

PID=`netstat -ntlpu | grep tcp | grep :48009 | awk '{print $NF}' | awk -F/ '{print $1}'`
if [ $PID ];then
  kill -9 $PID
fi


