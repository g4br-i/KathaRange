#include <iostream>
#include <random>
#include <vector>
#include <unistd.h>


int main(){
    std::random_device rd;
    std::default_random_engine r_eng(rd());
    std::uniform_int_distribution<> rnd_op(0,100);    // uniform random int distribution in [0,100] to select the operation
    std::uniform_int_distribution<> rnd_subnet(0,3);  // uniform random int distribution in [0,3] to select the subnet
    std::uniform_int_distribution<> rnd_sleep(5,30);  // uniform random int distribution in [5,30] to select the seconds between two operations
    std::uniform_int_distribution<> rnd_cnt(1,10);    // uniform random int distribution in [1,10] to select how many times an operation (e.g. ping) must be repeated
    std::vector<double> weights(33, 1.0);             // weights for a discrete distribution
    weights[1] = 10.0;
    weights[10] = 15.0;
    weights[20] = 12.0;
    weights[21] = 5.0;
    weights[30] = 5.0;
    // discrete distribution that gives more weight to the most common suffixes in this network's ip addresses
    std::discrete_distribution<> complete_addr(weights.begin(), weights.end()); 
    
    while (1){
        // selects a random operation and a random destination ip address
        int op = rnd_op(r_eng);
        std::string ip_addr = "192.168."+std::to_string(rnd_subnet(r_eng))+"."+std::to_string(complete_addr(r_eng)); 
        std::string command;
        if(op < 30){
            if(op < 10) command = "wget http://"+ip_addr;
            else command = "curl -s http://"+ip_addr;
        }
        else if(op < 50){
            if(op <= 35) command = "ping -c "+std::to_string(rnd_cnt(r_eng))+" -W 1 "+ ip_addr;
            else command = "hping3 --udp -c "+std::to_string(rnd_cnt(r_eng))+" "+ ip_addr;
        }
        else if(op < 70){
            command = "scp admin@"+ip_addr+" /shared/scripts/foo.txt";
        }
        else if(op < 90){
            command = "timeout 5 telnet "+ip_addr;
        }
        else{
            if(op < 95) command = "dig @1.1.1.1 example.com";
            else command = "nslookup example.com 1.1.1.1";
        }
        command = command + " > /dev/null 2>&1 &";
        system(command.c_str());
        sleep(rnd_sleep(r_eng));
    }
}
