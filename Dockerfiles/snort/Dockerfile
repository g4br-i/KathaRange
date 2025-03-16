# Use Ubuntu as the base image
#FROM debian:bookworm-slim
FROM kathara/quagga:latest
# Install dependencies and Snort
WORKDIR /root

RUN apt-get update &&     apt-get install -y     autoconf net-tools automake bison build-essential cmake curl flex wget iproute2 git libdumbnet-dev libhwloc-dev libhyperscan-dev libluajit-5.1-dev liblzma-dev libpcap-dev libpcre2-dev libssl-dev man-db pkg-config vim zlib1g-dev libnet1-dev libnetfilter-queue-dev libmnl-dev python3 pip iptables libnghttp2-dev libntirpc-dev nano zip syslog-ng &&     apt-get clean &&     git clone "https://github.com/snort3/libdaq.git" &&     cd libdaq &&     ./bootstrap &&     ./configure && make &&    make install &&     ldconfig &&     cd ../ # &&     rm -rf libdaq 
# Download community rules

WORKDIR /home/snorty
RUN mkdir -p examples snort3 src .vim/syntax .vim/colors &&     cd src &&     git clone "https://github.com/snort3/snort3.git" &&     cd snort3 &&     ./configure_cmake.sh --prefix=/home/snorty/snort3 &&     cd build &&     make -j$(nproc) install &&     cd /home/snorty &&     rm -rf src/ &&     echo 'if [[ ! $PATH =~ /home/snorty/snort3/bin ]]; then export PATH=$PATH:/home/snorty/snort3/bin; fi' >> ~/.bashrc &&     echo 'alias snort="snort -c /home/snorty/snort3/etc/snort/snort.lua"' >> ~/.bashrc &&     echo 'export TERM=xterm-256color' >> ~/.bashrc &&     mkdir snort3/etc/rules &&     cd snort3/etc/rules &&     curl -LO "https://snort.org/downloads/community/snort3-community-rules.tar.gz" &&     tar xzf snort3-community-rules.tar.gz snort3-community-rules/snort3-community.rules --strip=1 &&     rm snort3-community-rules.tar.gz


    #&& tar -xzf /tmp/snort3-community-rules.tar.gz -C /etc/snort/rules \
    #&& rm /tmp/snort3-community-rules.tar.gz

# Copy your Snort configuration files into the container
#COPY config/snort.conf /etc/snort/snort.conf
#COPY config/local.rules /etc/snort/rules/local.rules

# Expose necessary ports
EXPOSE 22 80 443 8000

# Set bash as the default entry point
ENTRYPOINT ["/bin/bash"]

