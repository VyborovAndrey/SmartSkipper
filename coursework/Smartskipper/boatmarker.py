from kivy.garden.mapview import MapMarker


class BoatMarker(MapMarker):
    def __init__(self, number, **kwargs):
        super(MapMarker, self).__init__(**kwargs)
        self.number = number