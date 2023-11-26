import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"

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
    
    def __init__(self, **kwargs):
        super(WindAnimation, self).__init__(**kwargs)
        self.winds = []
        Clock.schedule_interval(self.move_winds, 1/34.0)
        Clock.schedule_interval(partial(self.add_random_wind, 30), 0.1)

    
    def add_random_wind(self, angle,*args):
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
                         distance=30,
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
        self.add_widget(WindAnimation())

    def load(self, path, filename):
        data = open(str(os.path.join(path, filename[0])))
        xmldoc = minidom.parse(data)
        self.track = xmldoc.getElementsByTagName('trkpt')
        self.n_track = len(self.track)
        self.lon = self.track[0].attributes['lon'].value
        self.lat = self.track[0].attributes['lat'].value
        self.zoom = 15

        # times = xmldoc.getElementsByTagName('time')
        # start_point_time = datetime.strptime(times[1].firstChild.nodeValue[-9:-1], "%H:%M:%S")

    def on_play(self):
        if self.track is None:
            return
        old_marker = MapMarker(source = "media/rotated.png", lon = float(self.track[0].attributes['lon'].value), lat = float(self.track[0].attributes['lat'].value))
        for i in range(self.n_track-1):
            lon = float(self.track[i].attributes['lon'].value)
            lat = float(self.track[i].attributes['lat'].value)
            next_lon = float(self.track[i+1].attributes['lon'].value)
            next_lat = float(self.track[i+1].attributes['lat'].value)

            self.bearing_a_boat(lon, lat, next_lon, next_lat)
            marker = MapMarker(source = "media/rotated.png", lon = lon, lat = lat)
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
        if old_marker != None:
            self.remove_marker(old_marker)
    
    def bearing_a_boat(self, lon, lat, next_lon, next_lat):
        dLon = next_lon - lon
        y = math.sin(dLon) * math.cos(next_lat)
        x = math.cos(lat) * math.sin(next_lat) - math.sin(lat) * math.cos(next_lat) * math.cos(dLon)
        bearing = int(math.atan2(y, x) * 180 / 3.1415)
        boat = cv2.imread("coursework\Smartskipper\media\lodka.png", cv2.IMREAD_UNCHANGED)
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

        cv2.imwrite("coursework/Smartskipper/media/rotated.png", rotated_mat)

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
