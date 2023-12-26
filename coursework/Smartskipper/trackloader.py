from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App


class TrackLoader(FloatLayout):
    def __init__(self, **kwargs):
        super(FloatLayout, self).__init__(**kwargs)
        self._popup = None
    def load(self, filename):
        map = App.get_running_app().root.ids.mapview
        map.loadtrack(filename)
        self._popup.dismiss()

    def cancel(self):
        self._popup.dismiss()

    def show_load(self):
        if self._popup == None:
            self._popup = Popup(title="Choose gpx file of your sailing adventure", content=self,
                                size_hint=(0.9, 0.9))
        self._popup.open()