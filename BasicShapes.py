from abc import ABC, abstractmethod
from Utils import Ray, Vector3
import math


class Drawable(ABC):
    Bias = 0.05

    def __init__(self, Color, albedo, Reflective=False):
        self.Color = Color
        self.Albedo = albedo
        self.Reflective = Reflective

    # Check Drawable intersection with Ray and return CollisionBool,PointAtCollision,length
    @abstractmethod
    def CheckIntersection(self, ray: Ray):
        pass

    @abstractmethod
    def getNormal(self, point: Vector3):
        pass

    @abstractmethod
    def CheckPointInObject(self, point: Vector3):
        pass


class Box(Drawable):
    def __init__(self, Position: Vector3, DimensionX, DimensionY, DimensionZ, Color, Albedo, Reflective=False):
        Drawable.__init__(self, Color, Albedo, Reflective)
        self.Position: Vector3 = Position
        self.DimensionX = DimensionX
        self.DimensionY = DimensionY
        self.DimensionZ = DimensionZ
        self.Extents: Vector3 = Vector3(DimensionX, DimensionY, DimensionZ)
        self.BBmin: Vector3 = Position - self.Extents / 2
        self.BBmax: Vector3 = Position + self.Extents / 2

    def CheckPointInObject(self, Point:Vector3):
        return self.BBmin < Point < self.BBmax

    def CheckIntersection(self, ray: Ray):
        t1, t2, tnear, tfar = 0, 0, -math.inf, math.inf
        b1 = self.BBmin
        b2 = self.BBmax
        for i in range(3):
            if ray.direction[i] == 0:
                if ray.origin[i] < b1[i] or ray.origin[i] > b2[i]:
                    return False, [], -1, []
            else:
                t1 = (b1[i] - ray.origin[i]) / ray.direction[i]
                t2 = (b2[i] - ray.origin[i]) / ray.direction[i]
                if t1 > t2:
                    t1, t2 = t2, t1
                if t1 > tnear:
                    tnear = t1
                if t2 < tfar:
                    tfar = t2
                if tnear > tfar or tfar < 0:
                    return False, [], -1, []
        Point = ray.getPointAt(tnear)
        mult = -1 if self.CheckPointInObject(ray.origin) else 1
        return True, Point, tnear, mult * self.getNormal(Point)

    def getNormal(self, point: Vector3):
        Normal = []

        # min == 0 but computation errors and rounding off doesn't let it be so ...
        min = math.inf

        # X/2 Plane
        dist = abs(point[0] - self.Position[0] + self.DimensionX / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(1, 0, 0)
        # -X/2 Plane
        dist = abs(point[0] - self.Position[0] - self.DimensionX / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(-1, 0, 0)

        # Y/2 Plane
        dist = abs(point[1] - self.Position[1] + self.DimensionY / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(0, 1, 0)

        # -Y/2 Plane
        dist = abs(point[1] - self.Position[1] - self.DimensionY / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(0, -1, 0)

        # Z/2 Plane
        dist = abs(point[2] - self.Position[2] + self.DimensionZ / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(0, 0, 1)

        # -Z/2 Plane
        dist = abs(point[2] - self.Position[2] - self.DimensionZ / 2)
        if dist < min:
            min = dist
            # Rotation not included
            Normal = Vector3(0, 0, -1)

        return Normal


class Sphere(Drawable):

    def __init__(self, Center: Vector3, Radius, Color, albedo, Reflective=False):
        Drawable.__init__(self, Color, albedo, Reflective)
        self.Center = Center
        self.Radius = Radius

    def CheckIntersection(self, ray: Ray):
        # Get Line passing through Ray's Orgin and Circle Center
        origin_center: Vector3 = ray.origin - self.Center
        # (rayDirection.(RayOrgin - CircleCenter))^2 - (||RayOrgin - CircleCenter||^2 - radius^2 ) >= 0 then there is intersection
        a = ray.direction.dot(ray.direction)
        b = 2 * ray.direction.dot(origin_center)
        c = origin_center.dot(origin_center) - self.Radius * self.Radius
        disc = b * b - a * c * 4
        if disc > 0:
            # roots of equation is (-b +/- sqrt(Disc))/2a
            sqrtDisc = math.sqrt(disc)
            # roots
            root1 = (- b + sqrtDisc) / 2 * a
            root2 = (- b - sqrtDisc) / 2 * a
            # Closest intersection required
            product = root1 * root2

            # Both roots same sign
            if product > 0:

                # if one -tive both are -tive
                if root1 < 0:
                    return False, [], -1, []

                # Both roots +tive
                else:
                    root = root1 if root1 < root2 else root2

            # Both Roots different signs
            else:

                # root1 is greater than 0 => root2 is less than 0
                if root1 > 0:
                    root = root1

                # root1 is less than 0 => root2 is greater than 0
                else:
                    root = root2

            Point = ray.getPointAt(root)
            multiplier = -1 if self.CheckPointInObject(ray.origin) else 1
            return True, Point, root, self.getNormal(Point) * multiplier
        else:
            return False, [], -1, []

    def getNormal(self, point: Vector3):
        Point: Vector3 = point
        normal =  (Point - self.Center) * -1
        normal = normal.getNormalizedVector()
        return normal

    def CheckPointInObject(self, Point: Vector3):
        os = Point - self.Center
        return os.getLength() < self.Radius
