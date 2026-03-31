#! bin/bash


#cp /shared/snort3/snort3-community.rules /home/snorty/snort3/etc/rules/snort3-community.rules
cp /snort3/nfq_inline.lua /home/snorty/snort3/etc/snort/
cp /snort3/afpacket_inline.lua /home/snorty/snort3/etc/snort/


#/home/snorty/snort3/bin/snort -c /home/snorty/snort3/etc/snort/snort.lua -i eth0:eth1 --tweaks afpacket_inline -Q -D

/home/snorty/snort3/bin/snort -c /home/snorty/snort3/etc/snort/snort.lua --tweaks nfq_inline -l /snort3/logs/ -Q -i 1 -D

iptables -t nat -I PREROUTING -j NFQUEUE --queue-num 1
iptables -I INPUT -j NFQUEUE --queue-num 1
#iptables -I OUTPUT -j NFQUEUE --queue-num 1
iptables -I FORWARD -j NFQUEUE --queue-num 1

syslog-ng &
WAZUH_MANAGER='192.168.2.23' WAZUH_AGENT_NAME=$HOSTNAME dpkg -i /wazuh-agent_4.9.0-1_amd64.deb
cp /snort3/ossec.conf /var/ossec/etc/ossec.conf
service wazuh-agent start

#/shared/snort3/splunk/bin/splunk start --answer-yes --accept-license
