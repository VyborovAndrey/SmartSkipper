from random import random, randint
from windbackend import Wind, move_point
from kivy.clock import Clock
from kivy_garden.mapview import MapLayer
from functools import partial
from utility import azimuth
from kivy.core.window import Window

class WindAnimation(MapLayer):
    def __init__(self, angle, velocity, **kwargs):
        super(WindAnimation, self).__init__(**kwargs)
        width, height = Window.size
        self.height = height
        self.width = width
        self.winds = []
        self.angle = azimuth(-angle-90)
        self.velocity = velocity
        Clock.schedule_interval(self.move_winds, 1/34.0)
        Clock.schedule_interval(partial(self.add_random_wind), 0.1)

    def set_angle(self, angle):
        self.angle = azimuth(-angle-90)

    def set_velocity(self, velocity):
        self.velocity = velocity

    def add_random_wind(self, *args):
        random_part_of_screen = randint(0, 1)
        if self.angle > 0 and self.angle < 180:
            anchor_y = -100
        else:
            anchor_y = self.height + 100

        if self.angle > 90 and self.angle < 270:
            anchor_x = self.width + 100
        else:
            anchor_x = -100

            
        random_part_of_screen = randint(0, 1)
        newwind = Wind(
                         main_color=[255,255,255,0.6],
                         o_x = random()*self.width  * (random_part_of_screen * -1 + 1) + (random_part_of_screen * anchor_x),
                         o_y = random()*self.height * (random_part_of_screen) + (random_part_of_screen * -1 + 1) * anchor_y,
                         angle=self.angle,
                         distance=self.velocity*5,
                        )
        self.add_widget(newwind)
        self.winds.append(newwind)


    def move_winds(self,*args):

        for wind in self.winds:
            wind.o_x, wind.o_y = move_point(wind.o_x,wind.o_y,wind.angle,6)
            wind.main_color=[x for x in map(lambda y:y * 0.999, wind.main_color)]
            if wind.main_color[3] < 0.45:
                self.winds.remove(wind)
                self.remove_widget(wind)
                del wind