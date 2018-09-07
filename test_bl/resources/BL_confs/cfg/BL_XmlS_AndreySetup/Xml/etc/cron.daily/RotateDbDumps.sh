 # Notes : 
 # - 500Gb partition to be checked is mounted on /var/
 # - core dumps should be disabled with 'ulimit -c 0' setting in /etc/profile
 # - intermediate locations (/var/backup/) should be emptied immediately by incrond

COMMON_PARAMS=' --disk-pathname=/var/ --min-disk-space=20000'
LOGPATH='/var/log/dolphin/RotateDbDumps.log'


#astdbase intermediate location 
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/backup/astdbase/*dump* $COMMON_PARAMS >>$LOGPATH 2>&1
#replaydb intermediate location
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/backup/replaydb/*dump* $COMMON_PARAMS >>$LOGPATH 2>&1
#RAF intermediate location
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/backup/radar*/* $COMMON_PARAMS >>$LOGPATH 2>&1

#replaydb in FTP directory
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/ftp/backup/replay/*dump* $COMMON_PARAMS >>$LOGPATH 2>&1
#astdbase in FTP directory
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/ftp/backup/astd/*dump* $COMMON_PARAMS >>$LOGPATH 2>&1
#RAF in FTP directory
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/ftp/radar*/* $COMMON_PARAMS >>$LOGPATH 2>&1

#core dumps (should be disabled anyway)
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/log/dolphin/core_dumps/*dump* $COMMON_PARAMS >>$LOGPATH 2>&1

#videoserver logs
python /usr/bin/dolphin/RotateDbDumps.py --deleted-files-mask=/var/log/wdjt*/*.log $COMMON_PARAMS >>$LOGPATH 2>&1