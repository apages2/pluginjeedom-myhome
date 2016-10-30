#!/bin/bash
data=""
for var in "$@"
do
	data="${data}${var}&"
done	
curl -G -k -s "#ip_master#/plugins/myhome/core/php/jeemyhome.php" -d "apikey=#apikey#&${data}"
exit 0