#!/bin/bash
# add additional dependencies required for your solution here.
# for example:
# pip3 install mysql-client

set -e

python3 /submissionscript/this.py /scripts/ "$MYSQL_USER" mysql_container "$MYSQL_DATABASE" "$MYSQL_PASSWORD"

sleep infinity