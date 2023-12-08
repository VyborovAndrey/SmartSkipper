from kivy.properties import *
from kivy.event import EventDispatcher
from kivy.uix.widget import Widget
from kivy.metrics import *
from kivy.graphics import *
import math


piby180 = math.pi/180.0
# ------------------ KVector -------------------- #

class KVector(EventDispatcher):
    o_x = NumericProperty(0)
    o_y = NumericProperty(0)
    angle = NumericProperty(0)
    distance = NumericProperty(0)

    def get_to_x(self):
        return self.o_x + (math.cos(self.angle * piby180) * self.distance)

    def get_to_y(self):
        return self.o_y + (math.sin(self.angle * piby180) * self.distance)

    def set_to_x(self, to_x):
        self.angle = ((math.atan2(to_x - self.o_x, self.o_y - self.to_y)/piby180)+630.0 ) % 360.0 
        absx = abs(to_x-self.o_x) 
        absy = abs(self.to_y-self.o_y) 
        self.distance = math.sqrt((absx*absx)+(absy*absy))

    def set_to_y(self, to_y):
        self.angle = ((math.atan2(self.to_x - self.o_x, self.o_y - to_y)/piby180)+630.0 ) % 360.0 
        absx = abs(self.to_x-self.o_x) 
        absy = abs(to_y-self.o_y) 
        self.distance = math.sqrt((absx*absx)+(absy*absy))

    to_x = AliasProperty(
                         get_to_x,
                         set_to_x,
                         bind=['o_x','o_y','angle','distance']
                        )

    to_y = AliasProperty(
                         get_to_y,
                         set_to_y,
                         bind=['o_x','o_y','angle','distance']
                        )
        
def move_point(x,y,angle,distance):
    return  (
             x + (math.cos(angle * piby180) * distance),
             y + (math.sin(angle * piby180) * distance)
            )

# ------------ Wind -------------- #

class Windd(Widget,KVector):
    shaft_width = NumericProperty(cm(0.05))
    main_color = ListProperty([1,1,1,0.7])
    outline_color = ListProperty([0,0,0,0.0])
    outline_width = NumericProperty(cm(0.0))
    

    def __init__(self, *args, **kwargs):
        Widget.__init__(self,*args,**kwargs)
        KVector.__init__(self,*args,**kwargs)

        with self.canvas:
            self.icolor = Color(rgba=self.main_color)
            self.shaft = Line(width=self.shaft_width)

            self.ocolor = Color(rgba=self.outline_color)
            self.shaft_outline_left = Line(width=self.outline_width)
            self.shaft_outline_right = Line(width=self.outline_width)

            

        
        self.bind(
                  o_x=self.update_dims,
                  o_y=self.update_dims,
                  to_x=self.update_dims,
                  to_y=self.update_dims,
                  shaft_width=self.update_shaft_width,
                  outline_color=self.update_outline_color,
                  main_color=self.update_color,
                  outline_width=self.update_outline_width,
                  )
        self.update_dims()
        self.update_shaft_width()
        self.update_color()

    def update_shaft_width(self,*args):
        self.shaft.width = self.shaft_width

    def update_outline_width(self, *args):
        self.shaft_outline_right.width = self.outline_width
        self.shaft_outline_left.width = self.outline_width
    
    def update_outline_color(self, *args):
        self.ocolor.rgba = self.outline_color

    def update_color(self, *args):
        self.icolor.rgba = self.main_color


    def update_dims(self, *args):
        shaft_x1, shaft_y1 = move_point(self.o_x, self.o_y, self.angle, 0 / math.sqrt(2))
        shaft_x2, shaft_y2 = move_point(self.to_x, self.to_y, self.angle,
                                        - math.cos(0 / 2.0 * piby180) * 0)


        self.shaft.points = [shaft_x1, shaft_y1, shaft_x2, shaft_y2]

        shaft_ol_x1, shaft_ol_y1 = move_point(shaft_x1, shaft_y1, self.angle -90, self.shaft_width /0.6)
        shaft_ol_x2, shaft_ol_y2 = move_point(shaft_x2, shaft_y2, self.angle -90, self.shaft_width /0.6)

        shaft_or_x1, shaft_or_y1 = move_point(shaft_x1, shaft_y1, self.angle +90, self.shaft_width /0.6)
        shaft_or_x2, shaft_or_y2 = move_point(shaft_x2, shaft_y2, self.angle +90, self.shaft_width /0.6)

        self.shaft_outline_left.points = [shaft_ol_x1, shaft_ol_y1, shaft_ol_x2, shaft_ol_y2]
        self.shaft_outline_right.points = [shaft_or_x1, shaft_or_y1, shaft_or_x2, shaft_or_y2]
