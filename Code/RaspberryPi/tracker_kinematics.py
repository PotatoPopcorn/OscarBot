import numpy as np

class TrackerKinematics:
    def __init__(self):
        self.baseRotation = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.baseTranslation = np.array([[0], [0], [0]])
        self.baseTransformationMatrix = np.identity(4)

    def setRootPositionAndRotation(self, translation, rotation):
        translation = np.array(translation)
        rotation = np.array(rotation)
        self.baseRotation = rotation
        self.baseTranslation = translation.reshape(-1, 1)
        self.baseTransformationMatrix = np.hstack((self.baseRotation, self.baseTranslation))
        self.baseTransformationMatrix = np.vstack((self.baseTransformationMatrix, np.array([0, 0, 0, 1])))
        self.baseTransformationMatrix = np.linalg.inv(self.baseTransformationMatrix)
        self.baseRotation = np.linalg.inv(self.baseRotation)
        # print(self.baseTransformationMatrix)


    def getLocalPosition(self, position):
        position = np.hstack((position, np.array([1]))).reshape(-1, 1)
        # print(position)
        return np.matmul(self.baseTransformationMatrix, position).reshape(-1)[0:3].tolist()

    def getLocalRotation(self, rotation):
        return np.matmul(self.baseRotation, np.array(rotation))

