import ImageTracer # remove once get tuple not needed
# import RPi.GPIO as GPIO # leave commented out unless on RPi
import threading
import time

#constants
PEN_IS_UP = 0
PEN_IS_DOWN = 1

class robot_control:
    def __init__(self, path):
        self._current_x_pos = 0
        self._current_y_pos = 0
        self._path = path
        self._current_pen_pos = PEN_IS_UP
        self._event = threading.Event()
        self._thread = threading.Thread(target=self._draw_image)
        self._gpio_setup()

        
    def start_drawing(self):
        self._thread.start()


    def stop_drawing(self):
        self._event.set()


    def _gpio_setup(self):
        #setup gpio
        return


    # draws every curve in an image
    def _draw_image(self):
        for curve in self._path:
            self._draw_curve(curve)


    # draws a single curve
    def _draw_curve(self, curve):
        start = curve.start_point
        x0, y0 = ImageTracer.get_tuple(start) # remove once get tuple not needed
        self._go_to_position(x0, y0) # go to start of curve
        for segment in curve:
            if segment.is_corner:
                x1, y1 = ImageTracer.get_tuple(segment.c) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                self._pen_down()
                if not self._event.is_set():
                    self._go_to_position(x1, y1)
                if not self._event.is_set():
                    self._go_to_position(x2, y2)
                self._pen_up()
            else:
                x1, y1 = ImageTracer.get_tuple(segment.c1) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.c2) # remove once get tuple not needed
                x3, y3 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                self._pen_down()
                for t in range(1,11): # possible index oob, test later
                    t/=10
                    if not self._event.is_set():
                        self._go_to_position(self._get_x_position(t, x0, x1, x2, x3), self._get_y_position(t, y0, y1, y2, y3))
                self._pen_up()
            start = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
        
        self._reset_pen()
    

    def _reset_pen(self):
        self._go_to_position(0, 0)
    

    def _pen_down(self):
        print("pen down")


    def _pen_up(self):
        print("pen up")


    # moves robot to new position from current position
    # returns new position to update current_pos
    def _go_to_position(self, x_new, y_new):
        print("moving from x={} y={} to x={} y={}".format(self._current_x_pos, self._current_y_pos, x_new, y_new)) # here until motor control exists
        time.sleep(2) # time simulation
        self._current_x_pos = x_new
        self._current_y_pos = y_new


    # returns x position on a segment given points from the equation and time 0 <= t <= 1
    # corner segments are broken into 2 parts
    # x0, x1 and
    # x1, x2
    # if working on the x1, x2 part use those as parameters for x0, x1 respectively
    def _get_x_position(self, t, x0, x1, x2=-1, x3=-1):
        if t < 0 or t > 1:
            raise ValueError("t value not between 0 and 1")
        if(x2==-1 and x3==-1):
            return (1 - t) * x0 + t * x1
        else:
            return (1 - t) * ((1 - t) * ((1 - t) * x0 + t * x1) + t * ((1 - t) * x1 + t * x2)) + t * (
                    (1 - t) * ((1 - t) * x1 + t * x2) + t * ((1 - t) * x2 + t * x3))


    # returns y position on a segment given points from the equation and time 0 <= t <= 1
    # corner segments are broken into 2 parts
    # y0, y1 and
    # y1, y2
    # if working on the y1, y2 part use those as parameters for y0, y1 respectively
    def _get_y_position(self, t, y0, y1, y2=-1, y3=-1):
        if t < 0 or t > 1:
            raise ValueError("t value not between 0 and 1")
        if(y2==-1 and y3==-1):
            return (1 - t) * y0 + t * y1
        else:
            return (1 - t) * ((1 - t) * ((1 - t) * y0 + t * y1) + t * ((1 - t) * y1 + t * y2)) + t * (
                    (1 - t) * ((1 - t) * y1 + t * y2) + t * ((1 - t) * y2 + t * y3))


    # returns velocity between 2 x or y values
    # intended for velocity in 1 axis
    def _get_velocity(self, p0, p1):
        return p1 - p0
