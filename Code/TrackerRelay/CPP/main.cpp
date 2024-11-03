#include <cstdio>
#include <chrono>
#include <string>
#include <thread>

#include "SerialHandler.h"
#include "ViconConnection.h"

int main(int argc, char** argv) {
	if (argc < 2) {
		fprintf(stderr, "Needs an IP\n");
		exit(1);
	}
	SerialHandler serial = SerialHandler(9);
	std::string addr = std::string("localhost:801");
	ViconConnection vicon = ViconConnection(addr);
	while (true) {
		serial.sendMessageToAddress(argv[1], 4911, vicon.getObjectsInScene());
		//std::this_thread::sleep_for(std::chrono::milliseconds(1000));
	}
	return 0;
}