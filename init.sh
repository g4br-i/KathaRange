#! /bin/bash
set -e

# colors
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
MAGENTA='\033[35m'
CYAN='\033[36m'
RESET='\033[0m'

# dirs
ROOT_DIR="$(pwd)"
DEPS_DIR="$ROOT_DIR/deps/"
WAZUH_DIR="$DEPS_DIR/wazuh-docker"
CALDERA_DIR="$DEPS_DIR/caldera"
DOCKERFILES_DIR="$ROOT_DIR/Dockerfiles"
LAB_DIR="$ROOT_DIR/lab/"
LAB_LIGHT_DIR="$ROOT_DIR/lab_light/"
WAZUH_AGENT_FILE="wazuh-agent_4.9.0-1_amd64.deb"
WAZUH_TAG="v4.9.0-katha"
SNORT3_RULES_TAR_FILE="snort3-community-rules.tar.gz"
SNORT3_RULES_FILE="snort3-community.rules"


image_exists() {
    local image_name=$1
    if docker images -q "$image_name" > /dev/null 2>&1; then
        return 0 
    else
        return 1
    fi
}

prompt_user() {
    local action=$1
    echo -e ${YELLOW}
    read -p "$action (y/n): " choice
    echo -e ${RESET}
    case "$choice" in
        y|Y ) return 0 ;;  # User wants to continue with action
        n|N ) return 1 ;;  # User does not want to continue
        * ) echo -e "${RED}Invalid input. Please enter y or n.${RESET}" && prompt_user "$action" ;;  # Re-prompt for valid input
    esac
}

check_kathara() {
    if ! command -v kathara &> /dev/null; then
        echo -e "${YELLOW}Kathara is not installed.${RESET}"
        if ! prompt_user "Kathara is not installed. Do you want to install it?"; then
            echo -e "${RED}Kathara is required to run this script. Exiting.${RESET}"
            exit 1
         else
             sudo dpkg -i kathara_3.7.7-1jammy_amd64.deb
             echo -e "${GREEN}Kathara installation completed.${RESET}"
             return 0
         fi
    else
        echo -e "${GREEN}Kathara is already installed. Proceeding...${RESET}"
    fi
}

# Welcome message in ASCII Art (colored)
echo -e "${MAGENTA}"
cat << "EOF"
 _  __     _   _           ____                        
| |/ /__ _| |_| |__   __ _|  _ \ __ _ _ __   __ _  ___ 
| ' // _` | __| '_ \ / _` | |_) / _` | '_ \ / _` |/ _ \
| . \ (_| | |_| | | | (_| |  _ < (_| | | | | (_| |  __/
|_|\_\__,_|\__|_| |_|\__,_|_| \_\__,_|_| |_|\__, |\___|
                                            |___/      
            - a Kathara Framework Cyber Lab -
EOF
echo -e "${RESET}"

check_kathara

mkdir -p "$DEPS_DIR"

if [[ ! -d "$WAZUH_DIR" ]]; then
    echo -e "${BLUE}Cloning wazuh-docker at version 4.9.0 compatible with Kathara framework...${RESET}"
    if ! git clone https://github.com/g4br-i/wazuh-docker.git "$WAZUH_DIR"; then
        echo -e "${RED}Failed to clone wazuh-docker repository.${RESET}" >&2
        exit 1
    fi
else
    echo -e "${GREEN}Wazuh directory already exists: $WAZUH_DIR${RESET}"
fi

echo -e "${BLUE}Building images for Wazuh...${RESET}"
cd "$WAZUH_DIR" 

if git show-ref --verify --quiet refs/heads/v4.9.0-katha-branch; then
    echo -e "${GREEN}Branch 'v4.9.0-katha-branch' already exists${RESET}"
    git checkout "v4.9.0-katha-branch"
else
    echo -e "${YELLOW}Checking out new branch 'v4.9.0-katha-branch'...${RESET}"
    git checkout -b "$WAZUH_TAG-branch" "tags/$WAZUH_TAG"
fi

if image_exists "wazuh/wazuh-indexer:4.9.0" && image_exists "wazuh/wazuh-manager:4.9.0" && image_exists "wazuh/wazuh-dashboard:4.9.0"; then
    if ! prompt_user "Wazuh images already exist. Do you want to rebuild them?"; then
        echo -e "${GREEN}Using existing Wazuh images.${RESET}"
    else
        /bin/bash build-docker-images/build-images.sh -v 4.9.0
    fi
else
    /bin/bash build-docker-images/build-images.sh -v 4.9.0
fi

echo ''

if [[ -f "$LAB_DIR/shared/$WAZUH_AGENT_FILE" ]]; then
    if ! prompt_user "The $WAZH_AGENT_FILE file already exists. Do you want to download it again?"; then
        echo -e "${GREEN}Using existing .deb file.${RESET}"
    else
        echo -e "${BLUE}Downloading agent .deb file for Wazuh...${RESET}"
        wget --directory-prefix="$LAB_DIR/shared/" "https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/$WAZUH_AGENT_FILE"
        cp "$LAB_DIR/shared/$WAZUH_AGENT_FILE" "$LAB_LIGHT_DIR/shared/" 
    fi     
fi

if [[ ! -d "$CALDERA_DIR" ]]; then
    echo -e "${BLUE}Cloning caldera project...${RESET}"
    if ! git clone https://github.com/g4br-i/caldera.git --recursive "$CALDERA_DIR"; then
        echo -e "${RED}Failed to clone caldera repository.${RESET}" >&2
        exit 1
    fi
else
    echo -e "${GREEN}Caldera directory already exists: $CALDERA_DIR${RESET}"
fi


echo -e "${BLUE}\n Downloading Snort3 rules... ${RESET}"
if [[ -f "$LAB_DIR/shared/snort3/$SNORT3_RULES_FILE" ]]; then
    if ! prompt_user "The $SNORT3_RULES_FILE file already exists. Do you want to download it again?"; then
        echo -e "${GREEN}Using existing rules file for snort3.${RESET}"
    else
        echo -e "${BLUE}Downloading ...${RESET}"
        wget --directory-prefix="$DEPS_DIR" "https://www.snort.org/downloads/community/$SNORT3_RULES_TAR_FILE"
        tar -xvf "$SNORT3_RULES_TAR_FILE"
        cp "$DEPS_DIR/snort3-community-rules/$SNORT3_RULES_FILE" "$LAB_DIR/shared/snort3/"
        cp "$DEPS_DIR/snort3-community-rules/$SNORT3_RULES_FILE" "$LAB_LIGHT_DIR/shared/snort3/" 
    fi     
fi

echo -e "${BLUE}Building images for the lab...${RESET}"
services=( "snort" "tomcat" "caldera" "vuln_apache" "kali")

cd "$DOCKERFILES_DIR"

for service in "${services[@]}"; do
    echo -e "${YELLOW}Building service: $service...${RESET}"
    docker-compose -f build-images.yml build --no-cache "$service"
    

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully built: $service${RESET}"
    else
        echo -e "${RED}Failed to build: $service${RESET}" >&2
    fi
done
