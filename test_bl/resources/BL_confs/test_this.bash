#!/bin/bash


if [ -z "$param" ] 
then
	echo "NOTHING passed to the other script"
	exit 99 
else
	echo "${param} passed to the other script"
	exit 0 
fi
