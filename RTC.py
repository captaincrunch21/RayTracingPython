from BasicShapes import *
from Lights import *
from Render import *
from Utils import Vector3

# Game properties declaration Start
# Colors definition
white = Vector3(255, 255, 255)
black = Vector3(0, 0, 0)
red = Vector3(255, 0, 0)
blue = Vector3(0, 0, 255)
green = Vector3(0, 255, 0)

# Dummy Scene Containing only Sphere need to improve
Scene = [Sphere(Vector3(0, 45, -60), 20, blue, 0.9), Sphere(Vector3(0, -45, -60), 20, green, 0.9),
         Sphere(Vector3(45, 0, -60), 20, green, 0.9),Sphere(Vector3(0, 0, -60), 20, red, 0.9, True)]

Lights = [PointLight(Vector3(10, 0, -10), white, 1.0)]

# Window dimensions
width = 1000
fov = 1.57
aspectRatio = 1.7
height = int(aspectRatio * width)
nearPlane = 1

def Draw():
    camera = Camera(nearPlane, width, width, fov, Vector3(0, 0, 0))
    renderer = Render()
    renderer.setCamera(camera)
    renderer.setScene(Scene)
    renderer.setLight(Lights)
    renderer.RenderScene()


Draw()