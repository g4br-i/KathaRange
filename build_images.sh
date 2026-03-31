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
DOCKERFILES_DIR="$ROOT_DIR/Dockerfiles"
WAZUH_DIR="$DOCKERFILES_DIR/wazuh"
CALDERA_DIR="$DOCKERFILES_DIR/caldera"
LAB_DIR="$ROOT_DIR/labs/lab"
WAZUH_AGENT_FILE="wazuh-agent_4.9.0-1_amd64.deb"
SNORT3_RULES_FILE="snort3-community.rules"
SNORT3_RULES_TAR_FILE="snort3-community-rules.tar.gz"

#region functions
image_exists() {
    local image_name=$1
    if [[ -n $(docker images -q "$image_name" 2>/dev/null) ]]; then
        return 0 
    else
        return 1
    fi
}

prompt_user() {
    local action=$1
    echo -e "${YELLOW}"
    read -p "$action (y/n): " choice
    echo -e "${RESET}"
    case "$choice" in
        y|Y ) return 0 ;;  
        n|N ) return 1 ;;  
        * ) echo -e "${RED}Invalid input. Please enter y or n.${RESET}" && prompt_user "$action" ;;  
    esac
}

check_kathara() {
    if ! command -v kathara &> /dev/null; then
        echo -e "${YELLOW}Kathara is not installed.${RESET}"
        if ! prompt_user "Kathara is not installed. Do you want to install it?"; then
            echo -e "${RED}Kathara is required to run this script. Exiting.${RESET}"
            exit 1
        else
            echo -e "${YELLOW}Installing...${RESET}"
            sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 21805A48E6CBBA6B991ABE76646193862B759810
            sudo add-apt-repository ppa:katharaframework/kathara
            sudo apt update
            sudo apt install kathara
            echo -e "${GREEN}Kathara installation completed.${RESET}"
        fi
    else
        echo -e "${GREEN}Kathara is already installed. Proceeding...${RESET}"
    fi
}

check_dependency() {
    local dep_name=$1
    if ! command -v "$dep_name" &> /dev/null; then
        echo -e "${RED}$dep_name is not installed. Please install it before running this script.${RESET}"
        exit 1
    fi
}

check_and_download_file() {
    local file_path="$1"
    local download_url="$2"
    local target_dir="$3"

    # Se target_dir non esiste, lo crea come utente normale
    if [ ! -d "$target_dir" ]; then
        sudo -u "$SUDO_USER" mkdir -p "$target_dir"
    fi

    # Controlla se il file esiste già
    if [ ! -f "${target_dir}/$(basename "$file_path")" ]; then
        echo -e "${BLUE}Downloading $(basename "$file_path") to $target_dir as normal user...${RESET}"
        sudo -u "$SUDO_USER" wget --directory-prefix="$target_dir" "$download_url"
    else
        echo -e "${GREEN}File $(basename "$file_path") already exists in $target_dir${RESET}"
    fi
}

docker_build_image(){
    service=$1
    docker-compose -f build-images.yml build --no-cache "$service"
        
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully built: $service${RESET}"
    else
        echo -e "${RED}Failed to build: $service${RESET}" >&2
    fi
}
#endregion 

check_dependency "docker"

if ! command -v docker-compose &> /dev/null; then
   if ! prompt_user "docker-compose is needed to build the images proceed to add it to usr/local/bin?"; then
        echo -e "${RED}Cannot proceed without docker-compose.${RESET}"
        exit 1
    else
        echo 'docker compose --compatibility "$@"'|sudo tee /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    fi
fi

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

# --- Wazuh local ---
if [[ ! -d "$WAZUH_DIR" ]]; then
    echo -e "${RED}Local Wazuh Dockerfiles not found at $WAZUH_DIR. Exiting.${RESET}"
    exit 1
else
    echo -e "${GREEN}Using local Wazuh Dockerfiles: $WAZUH_DIR${RESET}"
fi

echo -e "${BLUE}Building Wazuh images...${RESET}"
cd "$WAZUH_DIR"

if image_exists "wazuh/wazuh-indexer:4.9.0" && image_exists "wazuh/wazuh-manager:4.9.0" && image_exists "wazuh/wazuh-dashboard:4.9.0"; then
    if ! prompt_user "Wazuh images already exist. Do you want to rebuild them?"; then
        echo -e "${GREEN}Using existing Wazuh images.${RESET}"
    else
        echo -e "${RED}To properly work the wazuh containers need  vm.max_map_count=262144${RESET}"
        sudo sysctl -w vm.max_map_count=262144
        /bin/bash build-images.sh -v 4.9.0 || exit 1
    fi
else
    /bin/bash build-images.sh -v 4.9.0 || exit 1
fi

echo ''

if compgen -G "$LAB_DIR/assets/*wazuh*" > /dev/null; then
    echo "Wazuh detected in lab."
    check_and_download_file "$LAB_DIR/assets/$WAZUH_AGENT_FILE" \
                            "https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/$WAZUH_AGENT_FILE" \
                            "$LAB_DIR/assets/"
else
    echo "No Wazuh folder found in lab. Skipping download."
fi

# --- Caldera local ---
if [[ ! -d "$CALDERA_DIR" ]]; then
    echo -e "${RED}Local Caldera Dockerfiles not found at $CALDERA_DIR. Exiting.${RESET}"
    exit 1
else
    echo -e "${GREEN}Using local Caldera Dockerfiles: $CALDERA_DIR${RESET}"
fi


RULES_DEST="$LAB_DIR/assets/snort3/rules"
LOCAL_RULES="$RULES_DEST/$SNORT3_RULES_FILE"
DOWNLOAD_TAR="$RULES_DEST/$SNORT3_RULES_TAR_FILE"
EXTRACT_DIR="$RULES_DEST/snort3-community-rules"

# Ensure destination exists
mkdir -p "$RULES_DEST"

if [[ -f "$LOCAL_RULES" ]]; then
    echo -e "${GREEN}Snort3 rules already exist in $RULES_DEST.${RESET}"
else
    # Download tarball only if not already present
    if [[ ! -f "$DOWNLOAD_TAR" ]]; then
        check_and_download_file "$DOWNLOAD_TAR" \
            "https://www.snort.org/downloads/community/$SNORT3_RULES_TAR_FILE" \
            "$RULES_DEST"
    fi

    # Extract in user-writable directory
    tar -xvf "$DOWNLOAD_TAR" -C "$RULES_DEST"
    chmod -R 755 "$EXTRACT_DIR"

    # Copy main rules file to destination
    cp "$EXTRACT_DIR/$SNORT3_RULES_FILE" "$RULES_DEST/"

    # Clean up extracted folder and tarball
    rm -rf "$EXTRACT_DIR"
    rm "$DOWNLOAD_TAR"

    echo -e "${GREEN}Downloaded and installed Snort3 rules to $RULES_DEST.${RESET}"
fi


echo -e "${BLUE}Building images for the lab...${RESET}"

services=( "snort" "tomcat" "caldera" "vuln_apache" "kali" "metasploitable")

cd "$DOCKERFILES_DIR"

for service in "${services[@]}"; do
    image="$service"

    if image_exists "$image"; then
        if prompt_user "Image $image already exists. Do you want to rebuild it?"; then
            echo -e "${YELLOW}Rebuilding $image...${RESET}"
            docker compose -f build-images.yml build --no-cache "$service"
        else
            echo -e "${GREEN}Using existing $image${RESET}"
        fi
    else
        echo -e "${YELLOW}Building missing image $image...${RESET}"
        docker compose -f build-images.yml build "$service"
    fi
done


