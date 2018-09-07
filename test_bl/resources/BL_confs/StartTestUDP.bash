#! /bin/bash
cd /usr/bin/dolphin/
#TMP=/tmp ./WatchDogServer --start --conf=/etc/dolphin/xml/mainTestUDP_only.xml >/var/log/dolphin/testUDP/stdout.txt 2>/var/log/dolphin/testUDP/stderr.txt
TMP=/tmp ./WatchDogServer --start --conf=/etc/dolphin/xml/mainTestUDP_only.xml 
