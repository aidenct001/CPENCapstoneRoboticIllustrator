import ImageTracer # remove once get tuple not needed
# import RPi.GPIO as GPIO # leave commented out unless on RPi
import threading
import time # maybe not needed | for testing currently

#constants
PEN_IS_UP = 0
PEN_IS_DOWN = 1

class RobotControl:
    def __init__(self, path = None):
        self._current_x_pos = 0
        self._current_y_pos = 0
        self._path = path
        self._current_pen_pos = PEN_IS_UP
        self._stop_event = threading.Event()
        self._running_event = threading.Event()
        self._thread = None
        self._gpio_setup()


    # starts the robot
    def start_drawing(self):
        if self._running_event.is_set():
            raise RunningException() # already started once
        self._running_event.set()
        self._thread = threading.Thread(target=self._draw_image)
        if(self._stop_event.is_set):
            self._stop_event.clear 
        self._thread.start()


    # interupts the drawing with a clean exit
    def stop_drawing(self):
        self._stop_event.set()


    # loads a new path object
    def load_path(self, path):
        self._path = path


    # checks if path has been loaded by user
    def is_loaded(self):
        return False if self._path == None else True


    # sets gpio default values
    def _gpio_setup(self):
        #setup gpio
        return


    # draws every curve in an image
    def _draw_image(self):
        for curve in self._path:
            if not self._stop_event.is_set():
                self._draw_curve(curve)


    # draws a single curve
    def _draw_curve(self, curve):
        start = curve.start_point
        x0, y0 = ImageTracer.get_tuple(start) # remove once get tuple not needed
        self._go_to_position(x0, y0) # go to start of curve
        self._pen_down()
        for segment in curve:
            if segment.is_corner:
                x1, y1 = ImageTracer.get_tuple(segment.c) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                if not self._stop_event.is_set():
                    self._go_to_position(x1, y1)
                if not self._stop_event.is_set():
                    self._go_to_position(x2, y2)
            else:
                x1, y1 = ImageTracer.get_tuple(segment.c1) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.c2) # remove once get tuple not needed
                x3, y3 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                for t in range(1,11):
                    t/=10
                    if not self._stop_event.is_set():
                        self._go_to_position(self._get_x_position(t, x0, x1, x2, x3), self._get_y_position(t, y0, y1, y2, y3))
            start = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
        self._pen_up()
        self._reset_pen()
        self._running_event.clear()


    # resets pen to 0,0 from current postion
    def _reset_pen(self):
        self._go_to_position(0, 0)
        self._stop_event.clear()
    

    # moves pen down if not already down
    def _pen_down(self):
        if(self._current_pen_pos == PEN_IS_DOWN):
            return
        # motor
        self._current_pen_pos = PEN_IS_DOWN
        print("pen down") # rm later


    # moves pen up if not already up
    def _pen_up(self):
        if(self._current_pen_pos == PEN_IS_UP):
            return
        # motor
        self._current_pen_pos = PEN_IS_UP
        print("pen up") # rm later


    # moves robot to new position from current position
    # updates current_pos to new position
    def _go_to_position(self, x_new, y_new):
        print("moving from x={} y={} to x={} y={}".format(self._current_x_pos, self._current_y_pos, x_new, y_new)) # here until motor control
        time.sleep(2) # time simulation for testing
        # motor
        self._current_x_pos = x_new
        self._current_y_pos = y_new


    # returns x position on a segment given points from the equation and time 0 <= t <= 1
    def _get_x_position(self, t, x0, x1, x2, x3):
        if t < 0 or t > 1:
            raise ValueError("t value not between 0 and 1")
        return (1 - t) * ((1 - t) * ((1 - t) * x0 + t * x1) + t * ((1 - t) * x1 + t * x2)) + t * (
                    (1 - t) * ((1 - t) * x1 + t * x2) + t * ((1 - t) * x2 + t * x3))


    # returns y position on a segment given points from the equation and time 0 <= t <= 1
    def _get_y_position(self, t, y0, y1, y2, y3):
        if t < 0 or t > 1:
            raise ValueError("t value not between 0 and 1")
        return (1 - t) * ((1 - t) * ((1 - t) * y0 + t * y1) + t * ((1 - t) * y1 + t * y2)) + t * (
                    (1 - t) * ((1 - t) * y1 + t * y2) + t * ((1 - t) * y2 + t * y3))


    # returns velocity between 2 x or y values
    # intended for velocity in 1 axis
    def _get_velocity(self, p0, p1):
        return p1 - p0


class RunningException(Exception):
    def __init__(self, message = ""):
        self.message = message
    def __str__(self):
        return self.message