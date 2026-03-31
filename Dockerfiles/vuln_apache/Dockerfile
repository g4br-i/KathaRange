# NOTE: This Docker image uses Apache version 2.4.49, which is known to have vulnerabilities.
# Specifically, this version is affected by CVE-2021-41773 and CVE-2021-42013, which allow path traversal and remote code execution.
# It is recommended to use a more recent version for production environments.

FROM httpd:2.4.49

# Puntiamo ai repository di archive.debian.org e ignoriamo la validità dei pacchetti
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list \
    && sed -i 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' /etc/apt/sources.list \
    && apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y iproute2 lsb-release vim procps curl syslog-ng netcat wget

COPY ./httpd.conf /usr/local/apache2/conf/

