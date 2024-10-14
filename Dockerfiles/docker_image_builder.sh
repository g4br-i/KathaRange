#!/bin/bash

GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

usage() {
    echo -e "${YELLOW}Usage: $0 <service-name> or $0 --all${RESET}"
    echo -e "${YELLOW}  <service-name>: Build the specified service.${RESET}"
    echo -e "${YELLOW}  --all: Build all services.${RESET}"
    exit 1
}

if [ -z "$1" ]; then
    usage  
fi

if [ "$1" == "--all" ]; then
    echo -e "${GREEN}Building all services...${RESET}"
    docker-compose -f build-images.yml build --no-cache
else
    echo -e "${GREEN}Building the specified service: ${YELLOW}$1${RESET}"
    docker-compose -f build-images.yml build $1 --no-cache
fi
