# NOTE: This Docker image uses Apache version 2.4.49, which is known to have vulnerabilities.
# Specifically, this version is affected by CVE-2021-41773 and CVE-2021-42013, which allow path traversal and remote code execution.
# It is recommended to use a more recent version for production environments.

FROM httpd:2.4.49
RUN apt update && apt install iproute2 lsb-release vim procps curl syslog-ng netcat curl wget -y
COPY ./httpd.conf /usr/local/apache2/conf/
