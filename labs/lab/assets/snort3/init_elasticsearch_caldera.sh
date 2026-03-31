echo 'waiting for opfs to be distributed'
#sleep 60

server="http://192.168.0.20:8888";
curl -s -X POST -H "file:elasticat.py" -H "platform:linux" $server/file/download > elasticat.py;
apt install -y python3-requests python3-dateutil;
python3 elasticat.py --server=$server --es-host="http://192.168.0.20:9200" --group=blue --minutes-since=60
