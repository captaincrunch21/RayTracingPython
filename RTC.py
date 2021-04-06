# imports
import numpy as np
import math
from PIL import Image
from abc import ABC, abstractmethod

#Game properties declaration Start
#Colors definition
white = [255,255,255]
black = [0,0,0]
red = [255,0,0]
blue = [0,0,255]
green = [0,255,0]

class Drawable(ABC):
    Bias = 0.05
    def __init__(self,Color,albedo,Reflective=False):
        self.Color = Color
        self.Albedo = albedo
        self.Reflective = Reflective

    #Check Drawable intersection with Ray and return CollisionBool,PointAtCollision,length
    @abstractmethod
    def CheckIntersection(self,ray):
        pass

    @abstractmethod
    def getNormal(self,point):
        pass

    @abstractmethod
    def CheckPointInObject(self,Point):
        pass

class Box(Drawable):
    def __init__(self,Position,DimensionX,DimensionY,DimensionZ,Color,Albedo,Reflective=False):
        Drawable.__init__(self,Color,Albedo,Reflective)
        self.Position = np.array(Position)
        self.DimensionX = DimensionX
        self.DimensionY = DimensionY
        self.DimensionZ = DimensionZ
        self.Extents = np.array([DimensionX,DimensionY,DimensionZ])
        self.BBmin =  Position - self.Extents/2
        self.BBmax =  Position + self.Extents/2

    def CheckPointInObject(self,Point):
         return self.BBmin[0] < Point[0] < self.BBmax[0] and self.BBmin[1] < Point[1] < self.BBmax[1] and self.BBmin[2] < Point[2] < self.BBmax[2]

    def CheckIntersection(self,ray):
        t1,t2,tnear,tfar = 0,0,-math.inf,math.inf
        b1 = self.BBmin
        b2 = self.BBmax
        for i in range(3):
            if ray.Direction[i]==0:
                ray.Orgin[i] < b1[i] or ray.Orgin[i] > b2[i]
                return False,[],-1,[]
            else:
                t1 = (b1[i] - ray.Orgin[i])/ray.Direction[i]
                t2 = (b2[i] - ray.Orgin[i])/ray.Direction[i]
                if t1>t2 :
                    t1,t2 = t2,t1
                if t1 > tnear:
                    tnear = t1
                if t2 <tfar:
                    tfar = t2
                if tnear >tfar or tfar <0 :
                    return False,[],-1,[]
        Point = ray.Orgin + tnear*ray.Direction
        mult =-1 if self.CheckPointInObject(ray.Orgin) else 1
        return True,Point,tnear,mult*self.getNormal(Point)


    def getNormal(self,point):
        Normal = []

        #min == 0 but computation errors and rounding off doesn't let it be so ...
        min = math.inf

        #X/2 Plane
        dist = abs(point[0] - self.Position[0] + self.DimensionX/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([1,0,0])
        #-X/2 Plane
        dist = abs(point[0] - self.Position[0] - self.DimensionX/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([-1,0,0])

        #Y/2 Plane
        dist = abs(point[1] - self.Position[1] + self.DimensionY/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([0,1,0])

        #-Y/2 Plane
        dist = abs(point[1] - self.Position[1] - self.DimensionY/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([0,-1,0])

        #Z/2 Plane
        dist = abs(point[2] - self.Position[2] + self.DimensionZ/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([0,0,1])

        #-Z/2 Plane
        dist = abs(point[2] - self.Position[2] - self.DimensionZ/2)
        if dist < min:
            min = dist
            #Rotation not included
            Normal = np.array([0,0,-1])

        return Normal



class Sphere(Drawable):

    def __init__(self,Center,Radius,Color,albedo,Reflective=False):
        Drawable.__init__(self,Color,albedo,Reflective)
        self.Center = np.array(Center)
        self.Radius = Radius

    def CheckIntersection(self,ray):
        # Get Line passing through Ray's Orgin and Circle Center
        OS = ray.Orgin - self.Center
        # (rayDirection.(RayOrgin - CircleCenter))^2 - (||RayOrgin - CircleCenter||^2 - radius^2 ) >= 0 then there is intersection
        a = np.dot(ray.Direction, ray.Direction)
        b = 2 * np.dot(ray.Direction, OS)
        c = np.dot(OS, OS) - self.Radius * self.Radius
        Disc = b * b - 4 * a * c
        if Disc>0:
            #roots of equation is (-b +/- sqrt(Disc))/2a
            sqrtDisc = math.sqrt(Disc)
            #roots
            root1 = (- b + sqrtDisc) / 2* a
            root2 = (- b - sqrtDisc) / 2* a
            #Closest intersection required
            product = root1*root2

            #Both roots same sign
            if product > 0:

                #if one -tive both are -tive
                if root1 < 0:
                     return False,[],-1,[]

                #Both roots +tive
                else:
                    root = root1 if root1 < root2 else root2

            #Both Roots different signs
            else:

                #root1 is greater than 0 => root2 is less than 0
                if root1 > 0:
                    root = root1

                #root1 is less than 0 => root2 is greater than 0
                else:
                    root = root2

            Point = np.add(ray.Orgin,np.multiply(ray.Direction,root))
            multiplier = -1 if self.CheckPointInObject(ray.Orgin) else 1
            return True,Point,root,multiplier*self.getNormal(Point)
        else:
            return False,[],-1,[]

    def getNormal(self,point):
        Point = np.array(point)
        normal = -1*(Point - self.Center)
        Normal = np.divide(normal,math.sqrt(np.dot(normal,normal)))
        return Normal

    def CheckPointInObject(self,Point):
        OS = Point - self.Center
        return math.sqrt(np.dot(OS,OS)) < self.Radius


class Ray:
    def __init__(self,Orgin,End):
        self.Orgin = np.array(Orgin)
        end = np.array(End)
        # this is not normalized
        Direction = np.subtract(Orgin,End)
        length = math.sqrt(sum([r**2 for r in Direction]))
        #Normalized Direction for easier Calculations
        self.Direction = -1*np.divide(Direction,length)

class Light(ABC):
    def __init__(self,Color,Power):
        self.Color = np.array(Color)
        self.Power = Power

    @abstractmethod
    def getShadowRayDirection(self,Point):
        pass

    @abstractmethod
    def getIntensityAtPoint(self,Point,Normal):
        pass


class DirectionalLight(Light):
    def __init__(self,Direction,Color,Power):
        Light.__init__(self,Color,Power)
        self.Direction = np.array(Direction)

    def getShadowRayDirection(self,Point):
        return -1*self.Direction

    def getIntensityAtPoint(self,Point,Normal):
        return max(0,np.dot(self.Direction,Normal))*self.Power

class PointLight(Light):
    def __init__(self,Position,Color,Power):
        Light.__init__(self,Color,Power)
        self.Position = np.array(Position)
        self.CutOff = 100

    def getShadowRayDirection(self,Point):
        return self.Position - Point

    def getIntensityAtPoint(self,Point,Normal):
        Direction =  -1* self.getShadowRayDirection(Point)
        DistanceFromLight = (Point - self.Position)
        PowerIndex = np.dot(DistanceFromLight,DistanceFromLight)
        return max(0,np.dot(Direction,Normal))*self.Power*(50/PowerIndex)

class AmbientLight(Light):
    def __init__(self,Color,Power):
        Light.__init__(self,Color,Power)

    def getShadowRayDirection(self,Point):
        return np.array([0,0,0])

    def getIntensityAtPoint(self,Point,Normal):
        return self.Power


class Camera:
    #Constructor
    def __init__(self,nearPlane,width,height,fov,Position):
        #Image Plane Pararmeters
        self.NearPlane = nearPlane
        #Image Pararmeters
        self.Width = width
        self.Height = height
        self.AspectRatio =width/height

        #Camera Parameters #ignoring Rotation for Now only translation
        self.Fov = fov
        self.Position = Position
        self.generateRays()


    FacingRatio = True
    #Rays passing from camera through every pixel in Image Plane
    Rays = []

    #Background Color
    Filler = white

    #Calculate Ray directions and populare Rays
    def generateRays(self):
        linSpacew = np.linspace(0.0,1.0,self.Width)
        linSpaceh = np.linspace(0.0,1.0,self.Height)
        for w in range(self.Width):
            for h in range(self.Height):
                #Normalizing Values between 0 to 1
                u = linSpacew[w]
                v = linSpaceh[h]
                #tan(fov/2) =  halfWidth/ClippingDistance
                halfImageWidth = math.tan(self.Fov/2)*self.NearPlane
                halfImageHeight = halfImageWidth/self.AspectRatio
                pixelPosition = [(1-2*u)*halfImageWidth,(1-2*v)*halfImageHeight,-self.NearPlane]
                #Creating Ray Object
                genRay = Ray(self.Position,pixelPosition)
                self.Rays.append(genRay)

    #Calculate Collision with nearest drawables present in Scene and color the pixels accordingly
    def GetRenderedPixels(self,scene,Lights):
        pixels = []
        for ray in self.Rays:
            #set ray collision to false at init
            rayCollided = False
            intersectedObj = None
            collisionPoint = []
            FinalColor = self.Filler
            coliisionDistance = math.inf
            ObjNormal = []
            for obj in scene:
                #checking for collision and or'ing.
                collisionValue,Point,Distance,norm = obj.CheckIntersection(ray)

                #Checking Collision is happening in ray direction not opposite
                if Distance>0 :
                    rayCollided = rayCollided or collisionValue

                #Checking for nearest collision
                if collisionValue and coliisionDistance >Distance :
                    coliisionDistance = Distance
                    collisionPoint = Point
                    intersectedObj = obj
                    ObjNormal = norm
                    #print(norm,Point)
            TotalIntensity = 0
            if rayCollided:
                for light in Lights:
                    intensity = light.getIntensityAtPoint(collisionPoint,ObjNormal)
                    shadowDir = light.getShadowRayDirection(collisionPoint)
                    #To handle Shadow acne
                    CheckPoint = collisionPoint - ObjNormal*intersectedObj.Bias
                    ShadowRay = Ray(CheckPoint ,CheckPoint+shadowDir)
                    shadowCollision = False
                    for shadowObj in scene:
                        shadowcollValue,shadowPoint,shadowDistance,shadownorm = shadowObj.CheckIntersection(ShadowRay)
                        if shadowcollValue:
                            intensity = 0
                    TotalIntensity += intensity

                TotalIntensity= min(TotalIntensity,1)
                FinalColor = [int(obj.Albedo*c*TotalIntensity) for c in intersectedObj.Color]

                if intersectedObj.Reflective:
                    #print("Checking Reflection")
                    CheckPoint = collisionPoint - ObjNormal*intersectedObj.Bias
                    #print(math.degrees(math.acos(np.dot(ray.Direction,ObjNormal))))
                    ReflectiveRayDirection = ray.Direction - 2*np.dot(ray.Direction,ObjNormal)*ObjNormal
                    ReflectedRay = Ray(CheckPoint,CheckPoint+ReflectiveRayDirection)
                    ReflectiveColor = intersectedObj.Color
                    ReflectiveCollided = False
                    RefDistance = math.inf
                    RefPoint = []
                    Refnorm = []
                    ReflectedObject = None
                    for ReflectiveObj in scene:
                        refcollValue,refPoint,refDistance,refnorm = ReflectiveObj.CheckIntersection(ReflectedRay)
                        ReflectiveCollided = ReflectiveCollided or refcollValue
                        if refcollValue and RefDistance>refDistance:
                            #print("Reflected")
                            ReflectiveColor = ReflectiveObj.Color
                            Distance = refDistance
                            Refnorm = refnorm
                            RefPoint = refPoint
                            ReflectedObject = ReflectiveObj

                    TotalIntensity = 0
                    if ReflectiveCollided:
                        TotalIntensity = 0
                        for light in Lights:
                            intensity = light.getIntensityAtPoint(RefPoint,Refnorm)
                            shadowDir = light.getShadowRayDirection(RefPoint)
                            #To handle Shadow acne
                            CheckPoint = RefPoint - Refnorm*ReflectedObject.Bias
                            ShadowRay = Ray(CheckPoint ,CheckPoint+shadowDir)
                            shadowCollision = False
                            for shadowObj in scene:
                                shadowcollValue,shadowPoint,shadowDistance,shadownorm = shadowObj.CheckIntersection(ShadowRay)
                                if shadowcollValue:
                                    intensity = 0
                            TotalIntensity += intensity

                    TotalIntensity= min(TotalIntensity,1)
                    RefColor = [int(ReflectiveObj.Albedo*c*TotalIntensity) for c in ReflectiveColor]
                    FinalColor = RefColor if ReflectiveCollided else FinalColor

            #setting Pixel Color

            pixel =  FinalColor
            pixels.extend(pixel)
        return pixels


class Render:
    def setCamera(self,camera):
        self.Camera = camera

    def setScene(self,scene):
        self.Scene = scene

    def setLight(self,light):
        self.Light = light

    def RenderScene(self):
        #Check Collisions with rays and get Draw Image from Pixel
        pixels = self.Camera.GetRenderedPixels(self.Scene,self.Light)
        pixels = bytes(pixels)
        img = Image.frombytes('RGB', (self.Camera.Width,self.Camera.Height), pixels)
        img.show()
        img.save("Result.jpg")


#Dummy Scene Containing only Sphere need to improve
#Scene = [Sphere([0,0,-40],20,red,0.9)]
Scene = [Sphere([0,45,-60],20,blue,0.9),Sphere([0,-45,-60],20,green,0.9),Sphere([45,0,-60],20,green,0.9),Sphere([0,0,-60],20,red,0.9,True)]
#Scene = [Box([0,0,-100],165,150,5,[100,100,100],1.0),Sphere([0,0,-40],20,red,0.8,True),Box([0,60,-40],150,5,100,[150,150,0],1.0),Box([0,-60,-40],150,5,100,[0,190,220],1.0,True),Box([-60,0,-40],5,100,100,green,1.0)]
Lights = [PointLight([10,0,-10],white,1.0)]
#Lights = [DirectionalLight([0.58,0.58,-0.58],white,0.8)]



#Window dimensions
width = 1000
fov = 1.57
aspectRatio = 1.7
height = int(aspectRatio*width)
nearPlane =1

def Draw():
    camera = Camera(nearPlane,width,width,fov,[0,0,0])
    renderer = Render()
    renderer.setCamera(camera)
    renderer.setScene(Scene)
    renderer.setLight(Lights)
    renderer.RenderScene()


Draw()
