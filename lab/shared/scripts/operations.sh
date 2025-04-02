#!/bin/bash

useradd -m -s /bin/bash admin -G root
echo "admin:admin" | chpasswd
service ssh start