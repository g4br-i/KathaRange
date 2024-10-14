FROM kalilinux/kali-rolling

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y iputils-ping net-tools iproute2
RUN apt-get install -y kali-linux-headless


# -- install powershell

RUN apt-get update && apt -y install powershell

SHELL ["pwsh", "-Command"]
# -- Install Atomic Red Team from pwsh
RUN IEX (IWR 'https://raw.githubusercontent.com/redcanaryco/invoke-atomicredteam/master/install-atomicredteam.ps1' -UseBasicParsing); \
    Install-AtomicRedTeam -getAtomics

RUN New-Item $PROFILE -Force

COPY ./setup.ps1 .
RUN ./setup.ps1

SHELL ["bin/zsh"]
