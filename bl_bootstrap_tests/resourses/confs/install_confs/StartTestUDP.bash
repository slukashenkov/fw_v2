#! /bin/bash
w_dog_srv=/usr/bin/dolphin/WatchDogServer
conf_file=/usr/bin/dolphin/install_confs/mainTestUDP_only.xml

#TMP=/tmp ./WatchDogServer --start --conf=/etc/dolphin/xml/mainTestUDP_only.xml >/var/log/dolphin/testUDP/stdout.txt 2>/var/log/dolphin/testUDP/stderr.txt
TMP=/tmp 
${w_dog_srv} --start --conf=${conf_file} 
