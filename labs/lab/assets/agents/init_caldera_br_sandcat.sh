server="http://192.168.0.20:8888"

# Wait until the HTTP server responds
until curl -sk --head --max-time 2 "$server" >/dev/null 2>&1; do
    #echo "[!] Server not ready, retrying in 5s..."
    sleep 5
done
#echo "[+] Server is reachable"

# Download agent with retry
while true; do
    agent=$(curl -svkOJ -X POST -H "file:sandcat.go" -H "platform:linux" "$server/file/download" 2>&1 \
            | grep -i "Content-Disposition" \
            | grep -io "filename=.*" \
            | cut -d'=' -f2 \
            | tr -d '"\r')
    if [[ -n "$agent" && -f "$agent" ]]; then
        echo "[+] Agent downloaded successfully: $agent"
        break
    else
        #echo "[!] Failed to download agent, retrying in 5s..."
        sleep 5
    fi
done

chmod +x "$agent"

# Start Blue agent
echo 'Starting blue agent...'
nohup ./"$agent" -server "$server" -group blue &> blue.out &


# Start Red agent
echo 'Starting red agent...'
nohup ./$agent -server $server &> red.out &
