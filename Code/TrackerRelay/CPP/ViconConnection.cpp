#include "ViconConnection.h"

ViconConnection::ViconConnection(std::string address)
{
	printf("Starting Vicon Connection to: %s\n", address.c_str());
	viconClient = std::make_unique<ViconDataStreamSDK::CPP::Client>();
	std::string iHateCpp = "localhost:801";
	printf("Result: %s\n", iHateCpp.c_str());
	viconClient->Connect(iHateCpp);
	viconClient->SetBufferSize(1);
	viconClient->EnableSegmentData();

	tryGetFrame();

	viconClient->SetStreamMode(ViconDataStreamSDK::CPP::StreamMode::ServerPush);
	viconClient->SetAxisMapping(
		ViconDataStreamSDK::CPP::Direction::Forward,
		ViconDataStreamSDK::CPP::Direction::Left,
		ViconDataStreamSDK::CPP::Direction::Up
	);
}

std::string ViconConnection::getObjectsInScene()
{
	tryGetFrame();
	int subjectCount = viconClient->GetSubjectCount().SubjectCount;
	std::stringstream objectResults;
	objectResults << "{";
	for (int i = 0; i < subjectCount; ++i) {
		std::string subName = viconClient->GetSubjectName(i).SubjectName;
		std::stringstream subDataStream;
		subDataStream << "[";
		int segCount = viconClient->GetSegmentCount(subName).SegmentCount;
		for (int j = 0; j < segCount; ++j)
		{
			std::stringstream segData;
			std::string segName = viconClient->GetSegmentName(subName, j).SegmentName;
			bool segOccluded = viconClient->GetSegmentGlobalTranslation(subName, segName).Occluded;
			std::string inScene;
			if (segOccluded) 
			{
				inScene = "false";
			}
			else
			{
				inScene = "true";
			}
			segData << "{\"segment_name\":\"" << segName << "\", ";
			segData << "\"in_scene\":" << inScene << ", ";
			segData << "\"location\":" << generateTransObj(subName, segName) << ",";
			segData << "\"rotation_euler\":" << generateEulerObj(subName, segName) << ",";
			segData << "\"rotation_quaternion\":" << generateQuatObj(subName, segName) << ",";
			segData << "\"rotation_matrix\":" << generateRotMatObj(subName, segName) << "}";
			subDataStream << segData.str() << ", ";
		}
		std::string subDataString = subDataStream.str();
		subDataString.pop_back();
		subDataString.pop_back();
		subDataString.append("]");
		objectResults << "\"" << subName << "\":" << subDataString << ", ";
	}
	std::string result = objectResults.str();
	result.pop_back();
	result.pop_back();
	result.append("}");
	return result;
}

std::string ViconConnection::generateTransObj(std::string subName, std::string segName)
{
	double transX = viconClient->GetSegmentGlobalTranslation(subName, segName).Translation[0];
	double transY = viconClient->GetSegmentGlobalTranslation(subName, segName).Translation[1];
	double transZ = viconClient->GetSegmentGlobalTranslation(subName, segName).Translation[2];
	std::stringstream result;
	result << "{\"X\":" << transX << ", \"Y\":" << transY << ", \"Z\":" << transZ << " }";
	return result.str();
}

std::string ViconConnection::generateEulerObj(std::string subName, std::string segName)
{
	double eulerX = viconClient->GetSegmentGlobalRotationEulerXYZ(subName, segName).Rotation[0];
	double eulerY = viconClient->GetSegmentGlobalRotationEulerXYZ(subName, segName).Rotation[1];
	double eulerZ = viconClient->GetSegmentGlobalRotationEulerXYZ(subName, segName).Rotation[2];
	std::stringstream result;
	result << "{\"X\":" << eulerX << ", \"Y\":" << eulerY << ", \"Z\":" << eulerZ << " }";
	return result.str();
}

std::string ViconConnection::generateQuatObj(std::string subName, std::string segName)
{
	double quatX = viconClient->GetSegmentGlobalRotationQuaternion(subName, segName).Rotation[0];
	double quatY = viconClient->GetSegmentGlobalRotationQuaternion(subName, segName).Rotation[1];
	double quatZ = viconClient->GetSegmentGlobalRotationQuaternion(subName, segName).Rotation[2];
	double quatW = viconClient->GetSegmentGlobalRotationQuaternion(subName, segName).Rotation[3];
	std::stringstream result;
	result << "{\"X\":" << quatX << ", \"Y\":" << quatY << ", \"Z\":" << quatZ << ", \"W\":" << quatW << " }";
	return result.str();
}

std::string ViconConnection::generateRotMatObj(std::string subName, std::string segName)
{
	double mat00 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[0];
	double mat01 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[1];
	double mat02 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[2];
	double mat10 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[3];
	double mat11 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[4];
	double mat12 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[5];
	double mat20 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[6];
	double mat21 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[7];
	double mat22 = viconClient->GetSegmentGlobalRotationMatrix(subName, segName).Rotation[8];
	std::stringstream result;
	result << "[[" << mat00 << ", " << mat01 << "," << mat02 << "], ";
	result << "[" << mat10 << ", " << mat11 << "," << mat12 << "], ";
	result << "[" << mat20 << ", " << mat21 << "," << mat22 << "]]";
	return result.str();
}

bool ViconConnection::tryGetFrame(int timeout)
{
	while (timeout > 0) {
		if (viconClient->GetFrame().Result == ViconDataStreamSDK::CPP::Result::Enum::Success)
		{
			return true;
		}
		--timeout;
	}
	return false;
}
