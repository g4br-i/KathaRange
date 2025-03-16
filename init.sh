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
    local file_path=$1
    local download_url=$2
    local target_dir=$3

    if [[ -f "$file_path" ]]; then
        if ! prompt_user "The file $(basename "$file_path") already exists. Do you want to download it again?"; then
            echo -e "${GREEN}Using existing file: $(basename "$file_path").${RESET}"
            return
        fi
    fi

    echo -e "${BLUE}Downloading $(basename "$file_path")...${RESET}"
    wget --directory-prefix="$target_dir" "$download_url"
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
check_dependency "git"
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
        echo -e "${RED}To properly work the wazuh containers need  vm.max_map_count=262144${RESET}"
        sudo sysctl -w vm.max_map_count=262144
        /bin/bash build-docker-images/build-images.sh -v 4.9.0 || exit 1
    fi
else
    /bin/bash build-docker-images/build-images.sh -v 4.9.0 || exit 1
fi

echo ''


check_and_download_file "$LAB_DIR/shared/$WAZUH_AGENT_FILE" "https://packages.wazuh.com/4.x/apt/pool/main/w/wazuh-agent/$WAZUH_AGENT_FILE" "$LAB_DIR/shared/"
#cp "$LAB_DIR/shared/$WAZUH_AGENT_FILE" "$LAB_LIGHT_DIR/shared/"

if [[ ! -d "$CALDERA_DIR" ]]; then
    echo -e "${BLUE}Cloning caldera project...${RESET}"
    if ! git clone https://github.com/g4br-i/caldera.git --recursive "$CALDERA_DIR"; then
        echo -e "${RED}Failed to clone caldera repository.${RESET}" >&2
        exit 1
    fi
else
    echo -e "${GREEN}Caldera directory already exists: $CALDERA_DIR${RESET}"
     if ! prompt_user "Do you want to remove it and clone it again?"; then
        echo -e "${GREEN}Skipping...${RESET}"
    else
        rm -rf "$CALDERA_DIR"
        if ! git clone https://github.com/g4br-i/caldera.git --recursive "$CALDERA_DIR"; then
            echo -e "${RED}Failed to clone caldera repository.${RESET}" >&2
            exit 1
        fi
    fi
fi

mkdir -p "$LAB_DIR/shared/snort3/rules"
#mkdir -p "$LAB_LIGHT_DIR/shared/snort3/rules"

check_and_download_file "$LAB_DIR/shared/snort3/$SNORT3_RULES_FILE" "https://www.snort.org/downloads/community/$SNORT3_RULES_TAR_FILE" "$DEPS_DIR"
tar -xvf "$DEPS_DIR/$SNORT3_RULES_TAR_FILE" -C "$DEPS_DIR"
cp "$DEPS_DIR/snort3-community-rules/$SNORT3_RULES_FILE" "$LAB_DIR/shared/snort3/rules"
#cp "$DEPS_DIR/snort3-community-rules/$SNORT3_RULES_FILE" "$LAB_LIGHT_DIR/shared/snort3/rules"

rm "$DEPS_DIR/$SNORT3_RULES_TAR_FILE"

cp -r "$LAB_DIR/shared/" "$LAB_LIGHT_DIR/"

echo -e "${BLUE}Building images for the lab...${RESET}"
services=( "snort" "tomcat" "caldera" "vuln_apache" "kali")

if [[ -f "$DOCKERFILES_DIR/.env" ]]; then
    set -a
    source "$DOCKERFILES_DIR/.env"
    set +a
else
    echo -e "${RED}.env file not found in $DOCKERFILES_DIR. Exiting.${RESET}"
    exit 1
fi

cd "$DOCKERFILES_DIR"

for service in "${services[@]}"; do
    service_var_name=$(echo "${service^^}_VERSION")
    service_version=${!service_var_name}

    if ! image_exists "$service:$service_version"; then
        echo -e "${YELLOW}Building service: $service:$service_version...${RESET}"
        docker_build_image "$service"

    else 
        if ! prompt_user "Service image $service:$service_version already exist. Do you want to rebuild it"; then
            echo -e "${GREEN}Using existing $service:$service_version image.${RESET}"
            
        else
            echo -e "${YELLOW}Building service: $service:$service_version...${RESET}"
            docker_build_image "$service"
        fi
    fi
done

if [[ -f "$LAB_DIR/lab.conf.template" ]]; then
    envsubst < "$LAB_DIR/lab.conf.template" > "$LAB_DIR/lab.conf"
    envsubst < "$LAB_LIGHT_DIR/lab.conf.template" > "$LAB_LIGHT_DIR/lab.conf"
    echo -e "${GREEN}Generated lab.conf with updated image versions.${RESET}"
else
    echo -e "${RED}lab.conf.template not found in $LAB_DIR. Exiting.${RESET}"
    exit 1
fi
