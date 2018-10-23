#!/bin/bash

export PYTHONPATH=/home/slon/Bl_FW_V2
export DISPLAY=:0

printenv

#python3.6 loader_sonata.py
python3.6 /home/slon/Bl_FW_V2/test_bl/test_loader.py -test_name ${1}