from abc import ABC, abstractmethod
from Utils import Vector3


class Light(ABC):
    def __init__(self, Color: Vector3, Power):
        self.Color: Vector3 = Color
        self.Power = Power

    @abstractmethod
    def getShadowRayDirection(self, Point: Vector3):
        pass

    @abstractmethod
    def getIntensityAtPoint(self, Point: Vector3, Normal: Vector3):
        pass


class DirectionalLight(Light):
    def __init__(self, Direction: Vector3, Color, Power):
        Light.__init__(self, Color, Power)
        self.Direction: Vector3 = Direction

    def getShadowRayDirection(self, Point: Vector3):
        return self.Direction * -1

    def getIntensityAtPoint(self, Point: Vector3, Normal: Vector3):
        return max(0, self.Direction.dot(Normal)) * self.Power


class PointLight(Light):
    def __init__(self, Position: Vector3, Color: Vector3, Power):
        Light.__init__(self, Color, Power)
        self.Position: Vector3 = Position
        self.CutOff = 100

    def getShadowRayDirection(self, Point: Vector3):
        return self.Position - Point

    def getIntensityAtPoint(self, Point: Vector3, Normal: Vector3):
        Direction = self.getShadowRayDirection(Point) * -1
        DistanceFromLight = (Point - self.Position)
        PowerIndex = DistanceFromLight.dot(DistanceFromLight)
        return max(0, Direction.dot(Normal)) * self.Power * (50 / PowerIndex)


class AmbientLight(Light):
    def __init__(self, Color: Vector3, Power):
        Light.__init__(self, Color, Power)

    def getShadowRayDirection(self, Point):
        return Vector3(0, 0, 0)

    def getIntensityAtPoint(self, Point: Vector3, Normal: Vector3):
        return self.Power
