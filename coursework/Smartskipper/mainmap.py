import os
# os.environ["KIVY_NO_CONSOLELOG"] = "0"

from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.garden.mapview import MapView
from functools import partial
from xml.dom import minidom 
import cv2
import json
from copy import copy
from datetime import timedelta

from utility import bearing, get_rotation_matrix

from windanimation import WindAnimation
from trackloader import TrackLoader
from windloader import WindLoader
from buoys import Buoys
from info import Info
from boatmarker import BoatMarker



class MapViewWidget(MapView):

    def __init__(self,  **kwargs):
        super(MapViewWidget, self).__init__(**kwargs)
        self.map_source.url = "https://api.maptiler.com/maps/ocean/{z}/{x}/{y}.png?key=PzWJbIhOZ5nCgZozMu3I"
        self.lon = 30.2
        self.lat = 59.9
        self.zoom = 10
        self.tracks = []
        self.tracks_len: list[int] = []
        self.winds_dict = {}

        self.markers = []
        self.old_markers = [] 
        self.time = -1
        self.event = None

        self.infos = []
        self.selected_boat = None

#-----Загрузка файла пути и файла ветра------#
    def loadtrack(self, filenames):
        for i, filename in enumerate(filenames):
            data = open(filename)
            xmldoc = minidom.parse(data)
            self.tracks.append(xmldoc.getElementsByTagName('trkpt'))
            self.tracks_len.append(len(self.tracks[i]))
            self.lon = (self.tracks[i][0].attributes['lon'].value)
            self.lat = (self.tracks[i][0].attributes['lat'].value)
            self.infos.append(Info())
        self.markers = [BoatMarker(0, source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.old_markers = [BoatMarker(0, source = "cache/rotated.png", lon = 0, lat = 0)]*len(self.tracks)
        self.zoom = 15
        self.add_buoys()
    
    def loadwind(self, filename):
        self.winds_dict = self.make_wind_dict_from_json(filename[0])
        wind_dir = self.winds_dict['0:00:00'][0]
        wind_speed = self.winds_dict['0:00:00'][1]
        self.wind_widget = WindAnimation(angle=wind_dir, velocity=wind_speed)
        self.add_widget(self.wind_widget)

#-----Плеер------#
    def on_play(self):
        if self.tracks == [] or self.winds_dict == {}:
            return
        self.play()

    def on_stop(self):
        if self.event is not None:
            self.stop()

    def go_back_in_time(self):
        if self.time > 20:
            self.time -= 20
        else:
            self.time = 0

    def go_forward_in_time(self):
        if self.time > 0:
            self.time += 20
        else:
            pass

    def play(self, *args):
        self.time += 1
        for k, track in enumerate(self.tracks):
            lon =      float(track[self.time-1].attributes['lon'].value)
            lat =      float(track[self.time-1].attributes['lat'].value)
            next_lon = float(track[self.time].attributes['lon'].value)
            next_lat = float(track[self.time].attributes['lat'].value)
            self.infos[k].update(lon, lat, next_lon, next_lat, int(self.winds_dict.get("0:00:00")[0]), self.time)
            self.markers[k] = BoatMarker(k, source = "cache/rotated.png", lon = next_lon, lat = next_lat)
        Clock.schedule_once(partial(self.update_boat_marker, self.markers, self.old_markers), 0.5)
        Clock.schedule_once(partial(self.update_info), 0.5)
        Clock.schedule_once(partial(self.update_canvas), 0.5)
        self.old_markers = copy(self.markers)
        if self.time < self.tracks_len[0] - 1:
            self.event = Clock.schedule_once(partial(self.play), 0.5)
        self.check_and_change_wind()

    def stop(self):
        Clock.unschedule(self.event)

#-----Маркер лодки------#
    def update_boat_marker(self, markers, old_markers, *args):
        for marker, old_marker in zip(markers, old_markers):
            self.bearing_a_boat(old_marker.lon, old_marker.lat, marker.lon, marker.lat)
            marker.reload()
            self.add_marker(marker)
            marker.bind(on_press=lambda x: self.select_boat(x))
            if old_marker is not None:
                self.remove_marker(old_marker)
    
    def bearing_a_boat(self, lon, lat, next_lon, next_lat):
        brng = -1 * bearing(lon, lat, next_lon, next_lat)
        boat = cv2.imread("media/lodka.png", cv2.IMREAD_UNCHANGED)
        rotated_mat = get_rotation_matrix(boat, brng)
        cv2.imwrite("cache/rotated.png", rotated_mat)
#-------Информация------#
    def select_boat(self, boat, **kwargs):
        self.selected_boat = boat.number

    def update_info(self, *args):
        if self.selected_boat is not None:
            self.parent.children[0].children[3].property_value = str(round(self.infos[self.selected_boat].courses[self.time%10]))
            self.parent.children[0].children[2].property_value = str(round(self.infos[self.selected_boat].attws[self.time%10]))
            self.parent.children[0].children[1].property_value = str(round(self.infos[self.selected_boat].speeds[self.time%10], 2)) + " kn"
            self.parent.children[0].children[0].property_value = str(round(self.infos[self.selected_boat].vmgs[self.time%10], 2)) + " kn"

    def update_canvas(self, *args):
        if self.selected_boat is not None:
            for i, canvas in enumerate(self.infos[self.selected_boat].canvases):
                i = 3 - i
                self.parent.children[0].children[i].color_1 = canvas[0]
                self.parent.children[0].children[i].color_2 = canvas[1]
                self.parent.children[0].children[i].color_3 = canvas[2]
                self.parent.children[0].children[i].color_4 = canvas[3]
                self.parent.children[0].children[i].color_5 = canvas[4]
                self.parent.children[0].children[i].color_6 = canvas[5]
                self.parent.children[0].children[i].color_7 = canvas[6]
                self.parent.children[0].children[i].color_8 = canvas[7]
                self.parent.children[0].children[i].color_9 = canvas[8]
                self.parent.children[0].children[i].color_10 = canvas[9]
                self.parent.children[0].children[i].color_11 = canvas[10]


#-----Буи------#
    def add_buoys(self):
        buoys = Buoys(self.tracks)
        upwind_buoy = buoys.get_upwind_buoy()
        left_start_buoy = buoys.get_left_start_buoy()
        right_start_buoy = buoys.get_right_start_buoy()
        self.add_marker(left_start_buoy)
        self.add_marker(right_start_buoy)
        self.add_marker(upwind_buoy)

#-----Ветер------#
    def make_wind_dict_from_json(self, filename):
        data = open(filename)
        wind = json.load(data)
        wind_dict = json.loads(wind)
        return wind_dict

    def check_and_change_wind(self):
        time = str(timedelta(seconds=self.time))
        if self.winds_dict.get(time) is not None:
            self.wind_dir = int(self.winds_dict.get(time)[0])
            self.wind_speed = int(self.winds_dict.get(time)[1])
            self.wind_widget.set_angle(self.wind_dir)
            self.wind_widget.set_velocity(self.wind_speed)

class MainMapApp(MDApp):
    def on_start(self):
        self.loadtrack_dialog = TrackLoader()
        self.loadwind_dialog = WindLoader()



if __name__ == "__main__":
    MainMapApp().run()
