echo 'waiting for opfs to be distributed'
sleep 60

server="http://192.168.0.20:8888";
agent=$(curl -svkOJ -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download 2>&1 | grep -i "Content-Disposition" | grep -io "filename=.*" | cut -d'=' -f2 | tr -d '"\r') && chmod +x $agent 2>/dev/null;
echo 'start blue agent'
nohup ./$agent -server $server -group blue &> blu.out &
echo 'start red agent'
nohup ./$agent -server $server &> red.out &
