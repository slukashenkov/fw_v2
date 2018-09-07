HOSTNAME_PREFIX=${HOSTNAME%.localdomain}_
DUMP_FILENAME=/var/backup/astdbase/${HOSTNAME_PREFIX}astdbase-dump_`date +%Y%m%d_%H%M%S`
/usr/bin/pg_dump --host=localhost --username=astdadmin --format=c --blobs --no-owner --no-privileges --table=* --file=$DUMP_FILENAME astdbase
