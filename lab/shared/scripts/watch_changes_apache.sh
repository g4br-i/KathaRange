#!/bin/bash

WATCH_DIR="/var/www/html"

inotifywait -m -e modify,create,delete,move "$WATCH_DIR" | while read path action file; do
    systemctl restart apache2
done