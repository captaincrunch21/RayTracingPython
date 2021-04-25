from Utils import Ray, Vector3
import numpy as np
import math
from Lights import Light
from PIL import Image
from collections.abc import Sequence
from BasicShapes import Drawable


class Camera:
    # Constructor
    def __init__(self, nearPlane, width, height, fov, Position: Vector3):
        # Image Plane Pararmeters
        self.NearPlane = nearPlane
        # Image Pararmeters
        self.Width = width
        self.Height = height
        self.AspectRatio = width / height

        # Camera Parameters #ignoring Rotation for Now only translation
        self.Fov = fov
        self.Position: Vector3 = Position
        self.generateRays()

    FacingRatio = True
    # Rays passing from camera through every pixel in Image Plane
    Rays = []

    # Background Color
    Filler = Vector3(255, 255, 255)

    @staticmethod
    def checkRaySceneCollision(ray: Ray, scene):
        ray_collided = False
        intersected_obj: Drawable = None
        collision_point = []
        collision_distance = math.inf
        obj_normal = []
        for obj in scene:
            # checking for collision and or'ing.
            collision_value, point, distance, norm = obj.CheckIntersection(ray)
            # Checking Collision is happening in ray direction not opposite
            if distance > 0:
                ray_collided = ray_collided or collision_value

            # Checking for nearest collision
            if collision_value and collision_distance > distance:
                collision_distance = distance
                collision_point = point
                intersected_obj = obj
                obj_normal = norm

        return ray_collided,intersected_obj,collision_point,obj_normal

    def getColorValueFromLight(self, lights: Sequence[Light], contact_point: Vector3, contact_normal: Vector3, bias, obj_color: Vector3, scene,obj_albedo):
        total_intensity = 0
        for light in lights:

            shadow_dir = light.getShadowRayDirection(contact_point)
            # To handle Shadow acne
            check_point = contact_point - contact_normal * bias
            shadow_ray = Ray(check_point, check_point + shadow_dir)
            shadowcoll_value, shadow_obj, shadow_point, shadow_normal = self.checkRaySceneCollision(shadow_ray,scene)
            intensity = 0 if shadowcoll_value else  light.getIntensityAtPoint(contact_point, contact_normal)
            total_intensity += intensity

        total_intensity = min(total_intensity, 1)
        color_constant = obj_albedo*total_intensity
        return obj_color*color_constant

    def checkReflectionsRecursively(self, contact_point, contact_normal, scene,bias, incident_ray: Ray, obj_color: Vector3, lights: Sequence[Light]):
        CheckPoint = contact_point - contact_normal * bias
        ReflectiveRayDirection = incident_ray.direction -  contact_normal * 2 * incident_ray.direction.dot(contact_normal)
        ReflectedRay = Ray(CheckPoint, CheckPoint + ReflectiveRayDirection)
        refcollValue, refObj, refPoint, refnorm = self.checkRaySceneCollision(ReflectedRay,scene)
        if refcollValue:
            ref_color = self.getColorValueFromLight(lights,refPoint,refnorm,bias,refObj.Color,scene,refObj.Albedo)
            return obj_color * 0.1 + ref_color * 0.9
        else:
            return obj_color



    # Calculate Ray directions and populate Rays
    def generateRays(self):
        lin_spaceW = np.linspace(0.0, 1.0, self.Width)
        lin_spaceH = np.linspace(0.0, 1.0, self.Height)
        for w in range(self.Width):
            for h in range(self.Height):
                # Normalizing Values between 0 to 1
                u = lin_spaceW[w]
                v = lin_spaceH[h]
                # tan(fov/2) =  halfWidth/ClippingDistance
                half_image_width = math.tan(self.Fov / 2) * self.NearPlane
                half_image_height = half_image_width / self.AspectRatio
                pixel_position = [(1 - 2 * u) * half_image_width, (1 - 2 * v) * half_image_height, -self.NearPlane]
                # Creating Ray Object
                gen_ray = Ray(self.Position, Vector3(pixel_position[0], pixel_position[1], pixel_position[2]))
                self.Rays.append(gen_ray)

    # Calculate Collision with nearest drawables present in Scene and color the pixels accordingly
    def GetRenderedPixels(self, scene, Lights):
        pixels = []
        for ray in self.Rays:
            # set ray collision to false at init
            final_color = self.Filler
            # Checking for initial Ray collision
            ray_collided, intersected_obj, collision_point, obj_normal = self.checkRaySceneCollision(ray, scene)

            if ray_collided:
                final_color = self.getColorValueFromLight(Lights, collision_point, obj_normal, intersected_obj.Bias, intersected_obj.Color, scene, intersected_obj.Albedo)

                if intersected_obj.Reflective:
                    final_color = self.checkReflectionsRecursively(collision_point, obj_normal, scene, intersected_obj.Bias, ray, intersected_obj.Color, Lights)


            # setting Pixel Color

            pixel = final_color.getAsIntegerList()
            pixels.extend(pixel)
        return pixels


class Render:
    def setCamera(self, camera: Camera):
        self.Camera: Camera = camera

    def setScene(self, scene):
        self.Scene = scene

    def setLight(self, lights: Sequence[Light]):
        self.Lights: Sequence[Light] = lights

    def RenderScene(self):
        # Check Collisions with rays and get Draw Image from Pixel
        pixels = self.Camera.GetRenderedPixels(self.Scene, self.Lights)
        pixels = bytes(pixels)
        img = Image.frombytes('RGB', (self.Camera.Width, self.Camera.Height), pixels)
        img.show()
        img.save("Result.jpg")