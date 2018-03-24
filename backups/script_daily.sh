#!/bin/bash

source /home/gams/gams/bin/activate && /home/gams/gams/manage.py dumpdata > /home/gams/gams/backups/daily/backup_$(date +%F_%R).json

# VERY DANGEROUS COMMAND! DO NOT CHANGE PATH!
ls /home/gams/gams/backups/daily -t -d $PWD/* | tail -n +3 | xargs rm --


