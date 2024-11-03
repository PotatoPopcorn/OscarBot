# Original Code from the Vicon SDK

from vicon_dssdk import ViconDataStream

class ViconConnection:
    def __init__(self, address:str = "localhost:801"):
        self.client = ViconDataStream.Client()
        self.client.Connect(address)
        self.client.SetBufferSize(1)
        self.client.EnableSegmentData()

        self.try_get_frame()

        self.client.SetStreamMode(ViconDataStream.Client.StreamMode.EServerPush)
        self.client.SetAxisMapping(ViconDataStream.Client.AxisMapping.EForward, ViconDataStream.Client.AxisMapping.ELeft,
                              ViconDataStream.Client.AxisMapping.EUp)

    def try_get_frame(self, timeout:int = 50):
        self.has_frame = False
        while not self.has_frame:
            try:
                if self.client.GetFrame():
                    self.has_frame = True
                timeout = - 1
                if timeout < 0:
                    break
            except ViconDataStream.DataStreamException as e:
                self.client.GetFrame()

    def get_objects_in_scene(self):
        self.try_get_frame()
        subjectNames = self.client.GetSubjectNames()
        objects_in_scene = dict()
        for subjectName in subjectNames:
            segmentNames = self.client.GetSegmentNames(subjectName)
            segments = list()
            for segmentName in segmentNames:
                segment_location = dict()
                segment_location["segment_name"] = segmentName
                segment_location["in_scene"] = not self.client.GetSegmentGlobalTranslation(subjectName, segmentName)[1]
                segment_location["location"] = self.client.GetSegmentGlobalTranslation(subjectName, segmentName)[0]
                segment_location["rotation_euler"] = self.client.GetSegmentGlobalRotationEulerXYZ(subjectName, segmentName)[
                    0]
                segment_location["rotation_quaternion"] = \
                    self.client.GetSegmentGlobalRotationQuaternion(subjectName, segmentName)[0]
                segment_location["rotation_matrix"] = self.client.GetSegmentGlobalRotationMatrix(subjectName, segmentName)[0]

                segments.append(segment_location)
            objects_in_scene[subjectName] = segments
        return objects_in_scene


