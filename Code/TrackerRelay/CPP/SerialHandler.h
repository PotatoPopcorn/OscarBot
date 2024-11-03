#pragma once

#include <algorithm>
#include <sstream>
#include <string>
#include <Windows.h>

class SerialHandler
{
public:
	SerialHandler(int comNumber);
	~SerialHandler();
	int sendMessageToAddress(std::string ip, unsigned short port, std::string payload);

private: 
	HANDLE serialHandle;
	std::string replaceAll(std::string str, const std::string& from, const std::string& to);
};

