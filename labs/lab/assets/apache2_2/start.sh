#! bin/bash

cp /apache2_2/ossec.conf /var/ossec/etc/ossec.conf

/var/ossec/bin/wazuh-control start