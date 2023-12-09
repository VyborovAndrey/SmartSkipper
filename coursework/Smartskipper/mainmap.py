import os
# os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.garden.mapview import MapView, MapMarker
from functools import partial
from xml.dom import minidom
import math
import cv2
import json
from copy import copy, deepcopy

from utility import bearing, get_rotation_matrix
from windanimation import *
from trackloader import TrackLoader


class MapViewWidget(MapView):

    def __init__(self,  **kwargs):
        super(MapViewWidget, self).__init__(**kwargs)
        self.map_source.url = "https://api.maptiler.com/maps/ocean/{z}/{x}/{y}.png?key=PzWJbIhOZ5nCgZozMu3I"
        self.lon = 30.2
        self.lat = 59.9
        self.zoom = 10
        self.tracks: list['NodeList'] = []  
        self.tracks_len: list[int] = []
        self.add_widget(WindAnimation(angle=0, velocity=5))
        
        self.markers = [MapMarker(source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.old_markers = [MapMarker(source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.time = -1
        self.event = None

    def load(self, filenames):
        for i, filename in enumerate(filenames):
            data = open(filename)
            xmldoc = minidom.parse(data)
            self.tracks.append(xmldoc.getElementsByTagName('trkpt'))
            self.tracks_len.append(len(self.tracks[i]))
            self.lon = (self.tracks[i][0].attributes['lon'].value)
            self.lat = (self.tracks[i][0].attributes['lat'].value)
        self.markers = [MapMarker(source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.old_markers = [MapMarker(source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.zoom = 15
        self.add_buoys()

        # times = xmldoc.getElementsByTagName('time')
        # start_point_time = datetime.strptime(times[1].firstChild.nodeValue[-9:-1], "%H:%M:%S")

    def on_play(self):
        if self.tracks is None:
            return
        self.play()
        # Для того, чтобы воспроизведение шло с реальной скоростью
        # next_lon = float(track[i+1].attributes['lon'].value)
        # next_lat = float(track[i+1].attributes['lat'].value)
        # next_point_time = datetime.strptime(times[i].firstChild.nodeValue[-9:-1], "%H:%M:%S") 
        # Clock.schedule_once(partial(map.update_boat_marker, marker, old_marker), (next_point_time - start_point_time).total_seconds())


    def play(self, *args):
        self.time += 1
        for k, track in enumerate(self.tracks):
            lon = float(track[self.time].attributes['lon'].value)
            lat = float(track[self.time].attributes['lat'].value)
            self.markers[k] = MapMarker(source = "cache/rotated.png", lon = lon, lat = lat)
        Clock.schedule_once(partial(self.update_boat_marker, self.markers, self.old_markers), 0.25)
        self.old_markers = copy(self.markers)
        if self.time < self.tracks_len[0] - 1:
            self.event = Clock.schedule_once(partial(self.play), 0.25)
    
    def on_stop(self):
        if self.event is not None:
            self.stop()

    def stop(self):
        Clock.unschedule(self.event)

    def go_back_in_time(self):
        if self.time > 10:
            self.time -= 10
        else:
            self.time = 0

    def go_forward_in_time(self):
        self.time += 10
    
    def update_boat_marker(self, markers, old_markers, *args):
        for marker, old_marker in zip(markers, old_markers):
            self.bearing_a_boat(old_marker.lon, old_marker.lat, marker.lon, marker.lat)
            marker.reload()
            self.add_marker(marker)
            if old_marker is not None:
                self.remove_marker(old_marker)
    
    def bearing_a_boat(self, lon, lat, next_lon, next_lat):
        brng = bearing(lon, lat, next_lon, next_lat) - 90
        boat = cv2.imread("media/lodka.png", cv2.IMREAD_UNCHANGED)
        rotated_mat = get_rotation_matrix(boat, brng)
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
