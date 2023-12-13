from math import cos, radians
from utility import bearing, find_distance

class Info:
    def __init__(self):
        self.courses = [0]*10
        self.attws = [0]*10
        self.speeds = [0]*10
        self.vmgs = [0]*10

    def update(self, lon, lat, next_lon, next_lat, wind_dir, time):
        course = bearing(lon, lat, next_lon, next_lat)
        distance = find_distance(lat, lon, next_lat, next_lon)
        speed = distance * 3600 * 0.54
        delta_alpha = abs(radians(course) - radians(wind_dir))
        vmg = speed * cos(delta_alpha)
        attw = course - wind_dir
        if attw >= 180:
            attw = 360 - attw
        self.courses[time%10] = course
        self.speeds[time%10] = speed
        self.vmgs[time%10] = vmg
        self.attws[time%10] = attw
        self.canvas_courses = self.count_for_canvas(self.courses, course)
        self.canvas_speeds = self.count_for_canvas(self.speeds, speed)
        self.canvas_vmgs = self.count_for_canvas(self.vmgs, vmg)
        self.canvas_attw = self.count_for_canvas(self.attws, attw)
        self.canvases = (self.canvas_courses, self.canvas_attw, self.canvas_speeds, self.canvas_vmgs)
    
    def count_for_canvas(self, param, center):
        countlist = [0]*11
        param = [round(elem) for elem in param]
        center = round(center)
        for i in range(len(countlist)):
            rgba = (0, 0, 0.1*param.count(center-5+i), 0.8)
            if rgba == (0, 0, 0, 0.8): rgba = (1, 1, 1, 1)
            countlist[i] = rgba
        return countlist