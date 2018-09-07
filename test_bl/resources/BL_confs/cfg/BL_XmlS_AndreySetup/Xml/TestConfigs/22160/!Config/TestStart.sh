#! /bin/bash
cd /usr/bin/dolphin/
TMP=/tmp ./StandaloneMainApp /etc/dolphin/22160/mainTest.xml >/var/log/dolphin/test/teststdout.txt 2>/var/log/dolphin/test/teststderr.txt
