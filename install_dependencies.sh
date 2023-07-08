#!/bin/bash

if which python3 >> /dev/null
then
	echo "Python3 exists. Continuing..."
else
	echo "Python3 could not be found. Please install python3 and try again. Exiting..."
	exit
fi

if which pip3 >> /dev/null
then
	echo "Pip3 exists. Continuing..."
else
	echo "Pip3 could not be found. Please install Pip3 and try again. Exiting..."
	exit
fi

pip3 install termcolor numpy