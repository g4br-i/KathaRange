#! bin/bash

cp /shared/snort3/nfq_inline.lua /home/snorty/snort3/etc/snort/
cp /shared/snort3/afpacket_inline.lua /home/snorty/snort3/etc/snort/

/home/snorty/snort3/bin/snort -c /home/snorty/snort3/etc/snort/snort.lua --tweaks afpacket_inline -L pcap -l /shared/logs/ -i eth0:eth1:eth2:eth3 -D
/home/snorty/snort3/bin/snort -c /home/snorty/snort3/etc/snort/snort.lua --tweaks afpacket_inline -i eth0:eth1:eth2:eth3 -D

#iptables -t nat -I PREROUTING -j NFQUEUE --queue-num 1
#iptables -I INPUT -j NFQUEUE --queue-num 1
#iptables -I FORWARD -j NFQUEUE --queue-num 1

syslog-ng --no-caps &
WAZUH_MANAGER='192.168.2.23' WAZUH_AGENT_NAME=$HOSTNAME dpkg -i /shared/wazuh-agent_4.9.0-1_amd64.deb
cp /shared/snort3/ossec.conf /var/ossec/etc/ossec.conf
cat /shared/snort3/rules/custom.rules >> /home/snorty/snort3/etc/rules/snort3-community.rules
service wazuh-agent start
