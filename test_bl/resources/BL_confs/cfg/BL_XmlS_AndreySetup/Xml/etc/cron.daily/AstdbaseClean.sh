echo "astdbase cleaning() started at" `date` >> /var/log/dolphin/AstdbaseClean.log 2>&1
psql --host=localhost --dbname=astdbase --username=astdadmin --command="select cleaning()" >/dev/null 2>>/var/log/dolphin/AstdbaseClean.log
echo "astdbase cleaning() started at" `date` >> /var/log/dolphin/AstdbaseClean.log 2>&1
