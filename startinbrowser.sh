#!/usr/bin/env bash

#python -m SimpleHTTPServer &
#PID=($(pidof -x python -m SimpleHTTPServer))
PID=$(python -m SimpleHTTPServer)

while ps -p $PID; do echo "sleeping" sleep 1; done ; echo "starting chrome" google-chrome localhost:8000/draw

#while [[ $? -ne 0 ]]; do
	#echo "NOT READY"
#done

#google-chrome localhost:8000/draw

#if [ $? -eq 0 ] ;
#then
	#google-chrome localhost:8000/draw

#else
#	echo "Not ready"
#fi