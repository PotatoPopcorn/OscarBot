#pragma once

#include <memory>
#include <sstream>
#include <string>

#include "DataStreamClient.h"

class ViconConnection
{
public:
	ViconConnection(std::string address);
	std::string getObjectsInScene();

private:
	std::string generateTransObj(std::string subName, std::string segName);
	std::string generateEulerObj(std::string subName, std::string segName);
	std::string generateQuatObj(std::string subName, std::string segName);
	std::string generateRotMatObj(std::string subName, std::string segName);
	bool tryGetFrame(int timeout = 50);
	std::unique_ptr<ViconDataStreamSDK::CPP::Client> viconClient;
};

