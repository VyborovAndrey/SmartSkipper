from math import sin, cos, atan2, radians, degrees, sqrt
import cv2
import bisect

def azimuth(degree):
    return degree%360 

def bearing(origin_lat, origin_lon, destination_lat, destination_lon):
    dLon = (destination_lon - origin_lon)
    x = cos(radians(destination_lat)) * sin(radians(dLon))
    y = cos(radians(origin_lat)) * sin(radians(destination_lat)) - sin(radians(origin_lat)) * cos(radians(destination_lat)) * cos(radians(dLon))
    brng = atan2(x,y)
    brng = degrees(brng)
    if brng < 0:
        brng = 360 + brng
    return brng

def bearingg(origin_lat, origin_lon, destination_lat, destination_lon):
    rad = atan2(destination_lat-origin_lat, destination_lon-origin_lon)
    angle = degrees(rad)
    brng = azimuth(angle)
    return brng

def find_distance(origin_lat, origin_lon, destination_lat, destination_lon):
    #радиус земли в километрах
    R = 6373.0
    origin_lat = radians(origin_lat)
    origin_lon = radians(origin_lon)
    destination_lat = radians(destination_lat)
    destination_lon = radians(destination_lon)
    dlon = destination_lon - origin_lon
    dlat = destination_lat - origin_lat
    a = sin(dlat / 2)**2 + cos(origin_lat) * cos(destination_lat) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

def get_rotation_matrix(image, angle):
        height, width = image.shape[:2]
        image_center = (width / 2, height / 2)

        rotation_mat = cv2.getRotationMatrix2D(image_center, angle, 1)
        
        radians_of_angle = radians(angle)
        sin_of_angle = sin(radians_of_angle)
        cos_of_angle = cos(radians_of_angle)
        bound_w = int((height * abs(sin_of_angle)) + (width * abs(cos_of_angle)))
        bound_h = int((height * abs(cos_of_angle)) + (width * abs(sin_of_angle)))
        
        rotation_mat[0, 2] += ((bound_w / 2) - image_center[0])
        rotation_mat[1, 2] += ((bound_h / 2) - image_center[1])
        rotated_mat = cv2.warpAffine(image, rotation_mat, (bound_w, bound_h))
        return rotated_mat

def rindex(lst, value):
    for i in reversed(lst):
         if i < value:
              return lst.index(i)

def index_greater_than(array, value):
    return bisect.bisect_right(array, value)