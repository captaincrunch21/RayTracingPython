import numpy as np


class Vector3:
    # Creates a numpy array of size 3 with the elements given
    def __init__(self, x, y, z):
        self.vector = np.array([x, y, z])

    def __getitem__(self, item):
        return self.vector[item]

    def __setitem__(self, key, value):
        self.vector[key] = value

    def __add__(self, other):
        added_values = self.vector + other.vector if self.__class__ == other.__class__ else self.vector + other
        return Vector3(added_values[0], added_values[1], added_values[2])

    def __sub__(self, other):
        subbed_values = self.vector - other.vector if self.__class__ == other.__class__ else self.vector - other
        return Vector3(subbed_values[0], subbed_values[1], subbed_values[2])

    def __truediv__(self, other):
        divideded_values = self.vector / other.vector if self.__class__ == other.__class__ else self.vector / other
        return Vector3(divideded_values[0], divideded_values[1], divideded_values[2])

    def __mul__(self, other):
        multiplied_values = self.vector * other.vector if self.__class__ == other.__class__ else self.vector * other
        return Vector3(multiplied_values[0], multiplied_values[1], multiplied_values[2])

    def isnan(self):
        if np.isnan(self.vector[0]) or np.isnan(self.vector[1]) or np.isnan(self.vector[2]):
            return True
        else:
            return False

    def dot(self, other) -> float:
        if self.__class__ == other.__class__:
            dot_values = np.dot(self.vector, other.vector)
            return float(dot_values)
        else:
            print("Debug:Got unimplemented in dot",other, type(other))
            pass

    def cross(self, other):
        if self.__class__ == other.__class__:
            cross_array = np.cross(self.vector, other.vector)
            return Vector3(*cross_array)
        else:
            pass

    def getLength(self):
        return np.sqrt(self.dot(self))

    def getNormalizedVector(self):
        return self / self.getLength()

    def __str__(self):
        return "({0}, {1}, {2})".format(self.vector[0], self.vector[1], self.vector[2])

    # these comparisions are purely for Bounding box operations only
    def __gt__(self, other):
        return (self.vector[0] > other.vector[0] and self.vector[1] > other.vector[1] and self.vector[2] > other.vector[
            2])

    def __ge__(self, other):
        return (self.vector[0] >= other.vector[0] and self.vector[1] >= other.vector[1] and self.vector[2] >= other.vector[
            2])

    def __lt__(self, other):
        return (self.vector[0] < other.vector[0] and self.vector[1] < other.vector[1] and self.vector[2] < other.vector[
            2])

    def __le__(self, other):
        return (self.vector[0] <= other.vector[0] and self.vector[1] <= other.vector[1] and self.vector[2] <= other.vector[
            2])

    def __eq__(self, other):
        return (self.vector[0] == other.vector[0] and self.vector[1] == other.vector[1] and self.vector[2] == other.vector[
            2])

    def getAsList(self):
        return [self.vector[0], self.vector[1], self.vector[2]]

    def getAsIntegerList(self):
        return [int(self.vector[0]), int(self.vector[1]), int(self.vector[2])]



class Ray:
    def __init__(self, origin: Vector3, end: Vector3):
        self.origin: Vector3 = origin
        self.direction: Vector3 = (end - origin).getNormalizedVector()

    def getPointAt(self, t):
        return self.origin + self.direction * t
