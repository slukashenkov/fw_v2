#!/bin/bash

w_dog_dir=/usr/bin/dolphin/WatchDogServer
conf_dir=/usr/bin/dolphin/sonata_confs/main_sonata.xml

#./WatchDogServer --start --conf=./sonata_confs/main_sonata.xml >/dev/null
${w_dog_dir} --start --conf=${conf_dir} >/dev/null
