#! /bin/bash
cd /usr/bin/dolphin/
TMP=/tmp ./WatchDogServer --start --conf=/etc/dolphin/Server.xml >/var/log/dolphin/stdout.txt 2>/var/log/dolphin/stderr.txt
