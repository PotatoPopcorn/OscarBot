#include "SerialHandler.h"

SerialHandler::SerialHandler(int comNumber)
{
	std::stringstream path;
	path << "\\\\.\\COM" << comNumber;

	serialHandle = CreateFileA(path.str().c_str(), GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);

	if (serialHandle == INVALID_HANDLE_VALUE) {
		fprintf(stderr, "INVALID HANDLE\n");
		exit(-1);
	}

	DCB serialParams = { 0 };
	serialParams.DCBlength = sizeof(serialParams);

	if (!GetCommState(serialHandle, &serialParams)) {
		CloseHandle(serialHandle);
		fprintf(stderr, "Couldn't retrieve COMM state\n");
		exit(-2);
	}

	serialParams.BaudRate = CBR_115200;
	serialParams.ByteSize = 8;
	serialParams.StopBits = ONESTOPBIT;
	serialParams.Parity = NOPARITY;

	if (!SetCommState(serialHandle, &serialParams)) {
		CloseHandle(serialHandle);
		fprintf(stderr, "Couldn't set COMM state\n");
		exit(-3);
	}

	COMMTIMEOUTS timeout = { 0 };
	timeout.ReadIntervalTimeout = 50;
	timeout.ReadTotalTimeoutConstant = 50;
	timeout.ReadTotalTimeoutMultiplier = 50;
	timeout.WriteTotalTimeoutConstant = 50;
	timeout.WriteTotalTimeoutMultiplier = 10;

	if (!SetCommTimeouts(serialHandle, &timeout)) {
		CloseHandle(serialHandle);
		fprintf(stderr, "Couldn't set COMM timeouts\n");
		exit(-4);
	}
}

SerialHandler::~SerialHandler()
{
	CloseHandle(serialHandle);
}

int SerialHandler::sendMessageToAddress(std::string ip, unsigned short port, std::string payload)
{
	payload = replaceAll(payload, "\\", "\\\\");
	payload = replaceAll(payload, "\r", "\\r");
	payload = replaceAll(payload, "\n", "\\n");
	payload = replaceAll(payload, "\"", "\\\"");
	std::stringstream generatedJson;
	generatedJson << "{\"ip\":\"" << ip << "\", \"port\":"<< port <<", \"payload\":\"" << payload << "\"}\r\n";
	std::string DataBuffer = generatedJson.str();
	DWORD dwBytesToWrite = (DWORD) DataBuffer.size();
	DWORD dwBytesWritten = 0;
	BOOL bErrorFlag = FALSE;

	bErrorFlag = WriteFile(serialHandle, DataBuffer.c_str(), dwBytesToWrite, &dwBytesWritten, NULL);

	if (!bErrorFlag) {
		fprintf(stderr, "Error Sending data %i\n", bErrorFlag);
		return -1;
	}
	else {
		if (dwBytesWritten != dwBytesToWrite) {
			printf("Error: dwBytesWritten != dwBytesToWrite\n");
			return -2;
		}
		else {
			printf("Wrote %d bytes to COM9 successfully.\n", dwBytesWritten);
		}
	}
	return 0;
}

std::string SerialHandler::replaceAll(std::string str, const std::string& from, const std::string& to) {
	// https://stackoverflow.com/questions/2896600/how-to-replace-all-occurrences-of-a-character-in-string
	size_t start_pos = 0;
	while ((start_pos = str.find(from, start_pos)) != std::string::npos) {
		str.replace(start_pos, from.length(), to);
		start_pos += to.length(); // Handles case where 'to' is a substring of 'from'
	}
	return str;
}
