import subprocess
import pyshark
import csv
import os
import pwd
from math import ceil
from datetime import datetime

# struct that maps a port into the service that uses that port
port_service_map = {
    20: "ftp-data",
    21: "ftp",
    22: "ssh",
    23: "telnet",
    25: "smtp",
    53: "dns",
    80: "http",
    110: "pop3",
    143: "imap",
    443: "https",
    445: "smb",
    993: "imaps",
    995: "pop3s",
    3306: "mysql",
    3389: "rdp",
    5432: "postgresql",
    6379: "redis",
    6667: "irc",
    8080: "http",
}

# struct that maps a tcp flag into the corresponding string
tcp_flags = {
    0x00: "NULL", 0x01: "FIN", 0x02: "SYN", 0x04: "RST", 0x08: "PSH", 0x10: "ACK", 0x11: "FIN", 0x12: "SYN-ACK", 0x14: "RST", 0x18: "PSH", 0x20: "URG", 0x40: "ECE", 0x80: "CWR", 0x100: "NS",
}

# Function that finds the user id and the group id of the owner of this script
def get_script_owner():
    file_path = __file__     # this script's path
    return os.stat(file_path).st_uid, os.stat(file_path).st_gid  # return user id and group id of the owner of this script

# Function that creates a copy of the .pcap file to have enough permissions to analyze it
def create_temp_pcap(pcap_path):
    temp_file = "/tmp/temp_pcap.pcap"  # temp file where the .pcap will be copied
    owner_uid, owner_gid = get_script_owner()   # get user id and group id of the script's owner
    try:
        subprocess.run(f"sudo cp {pcap_path} {temp_file}", shell=True, check=True) # copy the .pcap file
        subprocess.run(f"sudo chmod 644 {temp_file}", shell=True, check=True) # chmod on the temp file
        subprocess.run(f"sudo chown {owner_uid}:{owner_gid} {temp_file}", shell=True, check=True) # change the owner of the temp file 
    except FileNotFoundError:
        return ""
    return temp_file

# Function that deletes the copy of the .pcap file
def clear_tmp(temp_file):
    subprocess.run(f"rm -f {temp_file}", shell=True)

# Function that computes statistics on the last 100 connections registered for every connection
def get_stats_last_hundred(conns):
    ct_srv_src = {}
    last_services_src = {}
    ct_srv_dst = {}
    last_services_dst = {}
    ct_dst_ltm = {}
    last_conns_dst = {}
    ct_src_ltm = {}
    last_conns_src = {}
    ct_src_dport_ltm = {}
    last_conns_dport = {}
    ct_dst_src_ltm = {}
    last_conns_sport = {}
    ct_dst_sport_ltm = {}
    last_conns_sm = {}
    i = 0
    for key,value in conns.items():
        # ct_srv_src
        k = (value['src_ip'], value['service'])
        if k[1] != '-' and k not in last_services_src: last_services_src[k] = [i]
        elif k[1] != '-': 
            last_services_src[k] = [j for j in last_services_src[k] if i - j < 100]
            last_services_src[k].append(i)
        else: last_services_src[k] = []
        ct_srv_src[key] = len(last_services_src[k])

        # ct_srv_dst
        k = (value['dst_ip'], value['service'])
        if k[1] != '-' and k not in last_services_dst: last_services_dst[k] = [i]
        elif k[1] != '-': 
            last_services_dst[k] = [j for j in last_services_dst[k] if i - j < 100]
            last_services_dst[k].append(i)
        else: last_services_dst[k] = []
        ct_srv_dst[key] = len(last_services_dst[k])

        # ct_dst_ltm
        k = value['dst_ip']
        if k not in last_conns_dst: last_conns_dst[k] = [i]
        else: 
            last_conns_dst[k] = [j for j in last_conns_dst[k] if i - j < 100]
            last_conns_dst[k].append(i)
        ct_dst_ltm[key] = len(last_conns_dst[k])

        # ct_src_ltm
        k = value['src_ip']
        if k not in last_conns_src: last_conns_src[k] = [i]
        else: 
            last_conns_src[k] = [j for j in last_conns_src[k] if i - j < 100]
            last_conns_src[k].append(i)
        ct_src_ltm[key] = len(last_conns_src[k])

        # ct_src_dport_ltm
        k = (value['src_ip'], value['dst_port'])
        if k not in last_conns_dport: last_conns_dport[k] = [i]
        else: 
            last_conns_dport[k] = [j for j in last_conns_dport[k] if i - j < 100]
            last_conns_dport[k].append(i)
        ct_src_dport_ltm[key] = len(last_conns_dport[k])

        # ct_dst_sport_ltm
        k = (value['dst_ip'], value['src_port'])
        if k not in last_conns_sport: last_conns_sport[k] = [i]
        else: 
            last_conns_sport[k] = [j for j in last_conns_sport[k] if i - j < 100]
            last_conns_sport[k].append(i)
        ct_dst_sport_ltm[key] = len(last_conns_sport[k])

        # ct_dst_src_ltm
        k = (value['src_ip'],value['dst_ip'])
        if k not in last_conns_sm: last_conns_sm[k] = [i]
        else:
            last_conns_sm[k] = [j for j in last_conns_sm[k] if i - j < 100]
            last_conns_sm[k].append(i)
        ct_dst_src_ltm[key] = len(last_conns_sm[k])

        i += 1
    return {'ct_srv_src': ct_srv_src, 'ct_srv_dst': ct_srv_dst, 'ct_dst_ltm': ct_dst_ltm, 'ct_src_ltm': ct_src_ltm, 'ct_src_dport_ltm': ct_src_dport_ltm, 'ct_dst_sport_ltm': ct_dst_sport_ltm, 'ct_dst_src_ltm': ct_dst_src_ltm}

# Function that computes the average jitter time in milliseconds of a connection
def jitter(timestamps):
    if len(timestamps)>1:
        deltas = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps) - 1)]
        jitter = sum(abs(deltas[i+1]-deltas[i]) for i in range(len(deltas)-1)) / max(len(deltas)-1,1)
        return 1000*jitter
    else: return '-'

# Function that computes the average interarrival time in milliseconds between the packets of a connection
def interArrival(timestamps):
    if len(timestamps)>1:
        deltas = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps) - 1)]
        arrival = abs(sum(deltas)/max(len(deltas),1))
        return 1000*arrival
    else: return '-'

# Function that, given a .pcap file, creates a .csv file based on some features of the unsw_nb15 dataset  
def unsw_nb15_features(temp_file, output_csv):
    cap = pyshark.FileCapture(temp_file)
    connections = {}

    for pkt in cap:
        try:
            src_ip = pkt.ip.src  # Source ip address
            dst_ip = pkt.ip.dst  # Destination ip address
            highest_layer = pkt.highest_layer   # Highest layer of the packet 
            timestamp = datetime.strptime(pkt.sniff_time.strftime('%Y-%m-%d %H:%M:%S.%f'), '%Y-%m-%d %H:%M:%S.%f') # Timestamp of the packet
            pkt_len = int(pkt.length)
            ttl = int(pkt.ip.ttl)  # Time to live
            proto = pkt.transport_layer if pkt.transport_layer is not None else highest_layer # Protocol
            src_port = int(pkt[pkt.transport_layer].srcport)  # Source port
            dst_port = int(pkt[pkt.transport_layer].dstport)  # Destination port
            state = tcp_flags.get(int(pkt.tcp.flags, 16), pkt.tcp.flags) if proto == 'TCP' and hasattr(pkt.tcp,'flags') else "-"

            conn_key = (int(pkt[pkt.transport_layer].stream), proto)  # Id of the connection (i.e. an int auto-generated by pyshark that identifies the packets of the same connection)

            if dst_port in port_service_map:
                service = port_service_map[dst_port]
            elif src_port in port_service_map:
                service = port_service_map[src_port]
            else:
                if highest_layer.lower() not in ['data', 'frame', 'eth', 'ip', 'tcp']: service = highest_layer.lower() 
                else: service = '-'

            if conn_key not in connections:
                connections[conn_key] = {
                    'src_ip': src_ip,
                    'src_port': src_port,
                    'dst_ip': dst_ip,
                    'dst_port': dst_port,
                    'start_time': timestamp,
                    'end_time': timestamp,
                    'sbytes': 0,
                    'dbytes': 0,
                    'sttl': [],
                    'dttl': [],
                    'sloss': 0,
                    'dloss': 0,
                    'Spkts': 0,
                    'Dpkts': 0,
                    'state': state,
                    'service': service,
                    'swin': [],
                    'dwin': [],
                    'stcpb': 0,
                    'dtcpb': 0,
                    'smeansz': [],
                    'dmeansz': [],
                    'trans_depth': 0,
                    'res_bdy_len': 0,
                    'sjittimes': [],
                    'djittimes': [],
                    'syn_time': None,
                    'synack': None,
                    'ackdat': None,
                    'tcprtt': None,
                    'is_sm_ips_ports': 0,
                }
            conn = connections[conn_key]   # Adds the connection to the dictionary of the connections if the key doesn't exists
            conn['end_time'] = max(conn['end_time'], timestamp)
            if conn['state'] != "FIN": conn['state'] = state

            # Computes some statistics of the connection
            
            if state == "SYN": 
                conn['syn_time'] = timestamp
            elif state == "SYN-ACK":  
                conn['synack'] = timestamp
            elif state == "ACK":  
                conn['ackdat'] = timestamp
                
            if src_ip == dst_ip and src_port == dst_port: conn['is_sm_ips_ports'] = 1

            if src_ip == conn['src_ip']: 
                conn['sbytes'] += pkt_len
                conn['Spkts'] += 1
                conn['sttl'].append(ttl)
                conn['smeansz'].append(pkt_len)
                conn['sjittimes'].append(float(pkt.sniff_timestamp))
                if proto == 'TCP':
                    if hasattr(pkt.tcp, 'window_size_value'): conn['swin'].append(int(pkt.tcp.window_size_value))
                    if hasattr(pkt.tcp, 'analysis_duplicate_ack') or hasattr(pkt.tcp, 'analysis_retransmission'): conn['sloss'] += 1
                    if hasattr(pkt.tcp, 'seq'): conn['stcpb'] = int(pkt.tcp.seq)

            if src_ip == conn['dst_ip']: 
                conn['dbytes'] += pkt_len
                conn['Dpkts'] += 1
                conn['dttl'].append(ttl)
                conn['dmeansz'].append(pkt_len)
                conn['djittimes'].append(float(pkt.sniff_timestamp))
                if proto == 'TCP':
                    if hasattr(pkt.tcp, 'window_size_value'): conn['dwin'].append(int(pkt.tcp.window_size_value))
                    if hasattr(pkt.tcp, 'analysis_duplicate_ack') or hasattr(pkt.tcp, 'analysis_retransmission'): conn['dloss'] += 1
                    if hasattr(pkt.tcp, 'seq'): conn['dtcpb'] = int(pkt.tcp.seq)

            if pkt.highest_layer.lower() == "http":
                if hasattr(pkt.http, "content_length"):
                    conn['res_bdy_len'] += int(pkt.http.content_length)
                elif hasattr(pkt.http, "file_data"):
                    conn['res_bdy_len'] += len(pkt.http.file_data)
                if hasattr(pkt.http, "request"):
                    conn['trans_depth'] += 1
                elif hasattr(pkt.http, "response"):
                    conn['trans_depth'] -= 1 
                
            if proto == 'TCP': conn['tcprtt'] = abs(float(pkt.tcp.analysis_ack_rtt))
            else: conn['tcprtt'] = '-'

        except AttributeError:
            continue
        
    print("Last packet analyzed...")
    stats = get_stats_last_hundred(dict(sorted(connections.items(), key = lambda elem: elem[1]['end_time'])))
    print("Starting to write the csv file...")

    # write csv file
    with open(output_csv, 'w', newline='') as csvfile:
        fieldnames = [
                    'srcip', 'sport', 'dstip', 'dsport', 'proto', 'state', 'dur', 'sbytes', 'dbytes', 'sttl', 'dttl', 'sloss', 'dloss', 'service', 'Sload', 'Dload', 'Spkts', 'Dpkts', 'swin', 'dwin',
                    'stcpb', 'dtcpb', 'smeansz', 'dmeansz', 'trans_depth', 'res_bdy_len', 'Sjit', 'Djit', 'Stime', 'Ltime', 'Sintpkt', 'Dintpkt', 'tcprtt', 'syn_time', 'synack', 'ackdat', 'is_sm_ips_ports',
                    'ct_srv_src', 'ct_srv_dst', 'ct_dst_ltm', 'ct_src_ltm', 'ct_src_dport_ltm', 'ct_dst_sport_ltm', 'ct_dst_src_ltm',
                    ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for conn_key, conn_data in connections.items():
            duration = (conn_data['end_time'] - conn_data['start_time']).total_seconds()
            writer.writerow({
                'srcip': conn_data['src_ip'], # source ip address
                'sport': conn_data['src_port'], # source port
                'dstip': conn_data['dst_ip'], # dest ip address
                'dsport': conn_data['dst_port'], # dest port
                'proto': conn_key[1], # protocol 
                'state': conn_data['state'], # state
                'dur': duration, # duration of the connection
                'sbytes': conn_data['sbytes'], # bytes from the source
                'dbytes': conn_data['dbytes'], # bytes from the dest
                'sttl': sum(conn_data['sttl'])/max(len(conn_data['sttl']),1), # source average time to live
                'dttl': sum(conn_data['dttl'])/max(len(conn_data['dttl']),1), # dest average time to live
                'sloss': conn_data['sloss'], # number of packets lost or retransmitted from the src
                'dloss': conn_data['dloss'], # number of packets lost or retransmitted from the dest
                'service': conn_data['service'], # service (http, ftp, ...)
                'Sload': conn_data['sbytes']*8/ceil(duration) if duration > 0 else 0.0, # Source bit per second
                'Dload': conn_data['dbytes']*8/ceil(duration) if duration > 0 else 0.0, # dest bit per second
                'Spkts': conn_data['Spkts'], # number of packets transmitted from the src
                'Dpkts': conn_data['Dpkts'], # number of packets transmitted from the dest
                'swin': sum(conn_data['swin'])/max(len(conn_data['swin']),1), # average value of the src TCP window advertisement value
                'dwin': sum(conn_data['dwin'])/max(len(conn_data['dwin']),1), # average value of the dest TCP window advertisement value
                'stcpb': conn_data['stcpb'], # TCP sequence number of the source
                'dtcpb': conn_data['dtcpb'], # TCP sequence number of the dest
                'smeansz': sum(conn_data['smeansz'])/max(len(conn_data['smeansz']),1), # mean of the packet size transmitted by the src
                'dmeansz': sum(conn_data['dmeansz'])/max(len(conn_data['dmeansz']),1), # mean of the packet size transmitted by the dest
                'trans_depth': conn_data['trans_depth'], # pipelined depth into the connection of http request/response transaction
                'res_bdy_len': conn_data['res_bdy_len'], # size of the body of an http response
                'Sjit': jitter(conn_data['sjittimes']), # source jitter
                'Djit': jitter(conn_data['djittimes']), # dest jitter
                'Stime': conn_data['start_time'], # timestamp of the first packet
                'Ltime': conn_data['end_time'], # timestamp of the last packet
                'Sintpkt': interArrival(conn_data['sjittimes']), # average time between a packet and the next one from the src
                'Dintpkt': interArrival(conn_data['djittimes']), # average time between a packet and the next one from the dest
                'tcprtt': conn_data['tcprtt'], # round trip time
                'syn_time': conn_data['syn_time'], # timestamp of the ack packet
                'synack': conn_data['synack'], # timestamp of the synack packet
                'ackdat': conn_data['ackdat'], # timestamp of the ack packet
                'is_sm_ips_ports': conn_data['is_sm_ips_ports'], # 1 if srcip == destip && srcport == destport else 0
                'ct_srv_src': stats['ct_srv_src'][conn_key], # number of connections with the same src_ip that are using the same service in the last 100 connections
                'ct_srv_dst': stats['ct_srv_dst'][conn_key], # number of connections with the same dst_ip that are using the same service in the last 100 connections
                'ct_dst_ltm': stats['ct_dst_ltm'][conn_key], # number of connections with the same dst_ip in the last 100 connections
                'ct_src_ltm': stats['ct_src_ltm'][conn_key], # number of connections with the same src_ip in the last 100 connections
                'ct_src_dport_ltm': stats['ct_src_dport_ltm'][conn_key], # number of connection with the same src_ip and the same dest port in the last 100 connections
                'ct_dst_sport_ltm': stats['ct_dst_sport_ltm'][conn_key], # number of conections with the same dst_ip and the same src port in the last 100 connections
                'ct_dst_src_ltm': stats['ct_dst_src_ltm'][conn_key], # number of connections with the same src_ip and dest_ip in the last 100 connections
            })
    print(f"Features saved in: {output_csv}")

if __name__ == '__main__':
    temp = create_temp_pcap('../logs/log.pcap.1743610739')
    if temp != "": 
        unsw_nb15_features(temp,'../logs/unsw_nb15.csv')
    clear_tmp(temp)
