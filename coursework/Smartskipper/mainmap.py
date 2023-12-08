import os

os.environ["KIVY_NO_CONSOLELOG"] = "1"
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.garden.mapview import MapView, MapMarker, MapLayer
from functools import partial
from xml.dom import minidom
import math
import cv2
import json

from trackloader import TrackLoader

#Для ветра
from kivy.uix.floatlayout import FloatLayout
from random import random, randint
from wind import *

class WindAnimation(MapLayer):
    
    def __init__(self, angle, velocity, **kwargs):
        super(WindAnimation, self).__init__(**kwargs)
        self.winds = []
        Clock.schedule_interval(self.move_winds, 1/34.0)
        Clock.schedule_interval(partial(self.add_random_wind, angle - 90, velocity), 0.1)

    
    def add_random_wind(self, angle, velocity, *args):
        random_part_of_screen = randint(0, 1)
        if angle > 0 and angle < 180:
            anchor_y = -100
        else:
            anchor_y = self.height + 100

        if angle > 90 and angle < 270:
            anchor_x = self.width + 100
        else:
            anchor_x = -100

            
        random_part_of_screen = randint(0, 1)
        newwind = Windd(
                         main_color=[255,255,255,0.6],
                         o_x = random()*self.width  * (random_part_of_screen * -1 + 1) + (random_part_of_screen * anchor_x),
                         o_y = random()*self.height * (random_part_of_screen) + (random_part_of_screen * -1 + 1) * anchor_y,
                         angle=angle,
                         distance=velocity*5,
                        )
        self.add_widget(newwind)
        self.winds.append(newwind)


    def move_winds(self,*args):

        for wind in self.winds:
            wind.o_x, wind.o_y = move_point(wind.o_x,wind.o_y,wind.angle,6)
            wind.main_color=[x for x in map(lambda y:y * 0.999, wind.main_color)]
            wind.outline_color=[x for x in map(lambda y:y * 0.999, wind.outline_color)]
            if wind.main_color[3] < 0.45:
                self.winds.remove(wind)
                self.remove_widget(wind)
                del wind


class MapViewWidget(MapView):

    def __init__(self,  **kwargs):
        super(MapViewWidget, self).__init__(**kwargs)
        self.map_source.url = "https://api.maptiler.com/maps/ocean/{z}/{x}/{y}.png?key=PzWJbIhOZ5nCgZozMu3I"
        self.lon = 30.2
        self.lat = 59.9
        self.zoom = 10
        self.track = None
        self.add_widget(WindAnimation(angle=0, velocity=5))

    def load(self, path, filenames):
        self.tracks: list['NodeList'] = []  
        self.tracks_len: list[int] = []
        for i, filename in enumerate(filenames):
            data = open(filename)
            xmldoc = minidom.parse(data)
            self.tracks.append(xmldoc.getElementsByTagName('trkpt'))
            self.tracks_len.append(len(self.tracks[i]))
            self.lon = (self.tracks[i][0].attributes['lon'].value)
            self.lat = (self.tracks[i][0].attributes['lat'].value)
        self.zoom = 15

        # times = xmldoc.getElementsByTagName('time')
        # start_point_time = datetime.strptime(times[1].firstChild.nodeValue[-9:-1], "%H:%M:%S")

    def on_play(self):
        if self.tracks is None:
            return
        self.add_buoys()
        for k, track in enumerate(self.tracks):
            old_marker = MapMarker(source = "cache/rotated.png", lon = float(track[0].attributes['lon'].value), lat = float(track[0].attributes['lat'].value))
            for i in range(self.tracks_len[k]-1):
                lon = float(track[i].attributes['lon'].value)
                lat = float(track[i].attributes['lat'].value)
                # next_lon = float(track[i+1].attributes['lon'].value)
                # next_lat = float(track[i+1].attributes['lat'].value)

                marker = MapMarker(source = "cache/rotated.png", lon = lon, lat = lat)
                # next_point_time = datetime.strptime(times[i].firstChild.nodeValue[-9:-1], "%H:%M:%S") 
                # Для того, чтобы воспроизведение шло с реальной скоростью
                # Clock.schedule_once(partial(map.update, marker, old_marker),
                #                      (next_point_time - start_point_time).total_seconds())
                Clock.schedule_once(partial(self.update, marker, old_marker),
                                    i*0.25)
                old_marker = marker

    def update(self, marker, old_marker, *args):    
        self.bearing_a_boat(old_marker.lon, old_marker.lat, marker.lon, marker.lat)
        marker.reload()
        self.add_marker(marker)
        if old_marker is not None:
            self.remove_marker(old_marker)
    
    def bearing_a_boat(self, lon, lat, next_lon, next_lat):
        dLon = next_lon - lon
        y = math.sin(dLon) * math.cos(next_lat)
        x = math.cos(lat) * math.sin(next_lat) - math.sin(lat) * math.cos(next_lat) * math.cos(dLon)
        bearing = int(math.atan2(y, x) * 180 / 3.1415)
        boat = cv2.imread("media/lodka.png", cv2.IMREAD_UNCHANGED)
        height, width = boat.shape[:2]
        image_center = (width / 2, height / 2)
        
        rotation_mat = cv2.getRotationMatrix2D(image_center, bearing, 1)
        
        radians = math.radians(bearing)
        sin = math.sin(radians)
        cos = math.cos(radians)
        bound_w = int((height * abs(sin)) + (width * abs(cos)))
        bound_h = int((height * abs(cos)) + (width * abs(sin)))
        
        rotation_mat[0, 2] += ((bound_w / 2) - image_center[0])
        rotation_mat[1, 2] += ((bound_h / 2) - image_center[1])
        
        rotated_mat = cv2.warpAffine(boat, rotation_mat, (bound_w, bound_h))

        cv2.imwrite("cache/rotated.png", rotated_mat)

    def det_upwind_buoy_pos(self):
        upwind = []
        for i in range(len(self.tracks[0])):
            upwind.append(self.tracks[0][i].attributes['lat'].value)
        return max(upwind)
    
    def det_start_buoy_pos(self):
        start = []
        for track in self.tracks:
            start.append(track[0].attributes['lon'].value)
        return float(max(start)) + 0.002, float(min(start)) - 0.002

    def add_buoys(self):
        upwind_buoy = MapMarker(source = "media/upwind_buoy.png", lon = float(self.tracks[0][0].attributes['lon'].value), lat = float(self.det_upwind_buoy_pos()))
        left_start_buoy  = MapMarker(source = "media/start_buoy.png", lon = float(self.det_start_buoy_pos()[0]), lat = float(self.tracks[0][0].attributes['lat'].value))
        right_start_buoy = MapMarker(source = "media/start_buoy.png", lon = float(self.det_start_buoy_pos()[1]), lat = float(self.tracks[0][0].attributes['lat'].value))
        self.add_marker(left_start_buoy)
        self.add_marker(right_start_buoy)
        self.add_marker(upwind_buoy)

class MainMapApp(MDApp):
    def on_start(self):
        self.load_dialog = TrackLoader()


class Wind():
    def load_wind(self, path, filename):
        wind_json = open(str(os.path.join(path, filename[0])))
        self.wind = json.loads(wind_json)


    def show_wind(self):
        pass

if __name__ == "__main__":
    MainMapApp().run()
