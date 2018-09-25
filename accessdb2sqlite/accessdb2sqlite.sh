#!/bin/bash

# converts Microsoft Access Databases to sqlite3 databases
# specific to data from Partners Healthcate 
# (removes one strange comment table)
# requires sqlite3 and mdbtools (https://github.com/brianb/mdbtools)
# mhalle@bwh.harvard.edu    2018-07-30

if [ $# -ne 2 ]; then
    echo "$0: usage is: $0 accessdb sqlitedb"
    exit 1
fi

ACCESSDB="$1"
SQLITEDB="$2"

if [ -f "${SQLITEDB}" ]; then
    echo "$0: error: sqlite db file ${SQLITEDB} exists."
    exit 1
fi

# extract metadata from accessdb
schema=$(mdb-schema "${ACCESSDB}" sqlite)
if [ $? -ne 0 ]; then
    exit 1
fi

tables=$(mdb-tables -1 "${ACCESSDB}" | grep -v '<--')
if [ $? -ne 0 ]; then
    exit 1
fi

# create the schema first
sqlite3 "${SQLITEDB}" <<< "${schema}"

# then export all the tables from access and immediately import them
for table in ${tables}; do
    mdb-export -I sqlite "${ACCESSDB}" "${table}" | sqlite3 "${SQLITEDB}"
done
