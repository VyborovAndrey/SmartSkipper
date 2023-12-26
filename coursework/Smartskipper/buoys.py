from kivy_garden.mapview import MapMarker


class Buoys:
    def __init__(self, tracks):
        self.tracks = tracks
        self.upwind_buoy = None
        self.left_start_buoy = None
        self.right_start_buoy = None
        self.make_buoys()

    def get_upwind_buoy(self):
        return self.upwind_buoy
    
    def get_left_start_buoy(self):
        return self.left_start_buoy
    
    def get_right_start_buoy(self):
        return self.right_start_buoy
    
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

    def make_buoys(self):
        self.upwind_buoy = MapMarker(source = "media/upwind_buoy.png", lon = float(self.tracks[0][0].attributes['lon'].value), lat = float(self.det_upwind_buoy_pos()))
        self.left_start_buoy  = MapMarker(source = "media/start_buoy.png", lon = float(self.det_start_buoy_pos()[0]), lat = float(self.tracks[0][0].attributes['lat'].value))
        self.right_start_buoy = MapMarker(source = "media/start_buoy.png", lon = float(self.det_start_buoy_pos()[1]), lat = float(self.tracks[0][0].attributes['lat'].value))