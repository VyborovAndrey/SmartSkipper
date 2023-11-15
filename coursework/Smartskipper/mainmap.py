from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.garden.mapview import MapView, MapMarker
from functools import partial
from xml.dom import minidom
from datetime import datetime
import math
import cv2
import os

from trackloader import TrackLoader

class MapViewWidget(MapView):

    def __init__(self,  **kwargs):
        super(MapViewWidget, self).__init__(**kwargs)
        self.lon = 30.2
        self.lat = 59.9
        self.zoom = 10
        self.track = None
    
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
        if self.track == None:
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
        boat = cv2.imread("media/Lodka.png", cv2.IMREAD_UNCHANGED)
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

        cv2.imwrite("media/rotated.png", rotated_mat)

class MainMapApp(MDApp):
    def on_start(self):
        self.load_dialog = TrackLoader()


if __name__ == "__main__":
    MainMapApp().run()
