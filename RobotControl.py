import ImageTracer # remove once get tuple not needed
import RPi.GPIO as GPIO

class robot_control:
    def __init__(self):
        self.current_x_pos = 0
        self.current_y_pos = 0
        # currently sets to 0 no matter what position motors are in. Maybe include a reset that is not based on a position but idk how. If the code exits well I can move back based on current position but that is not a good solution
        self.gpio_setup()


    def gpio_setup(self):
        #setup gpio
        return


    # draws every curve in an image
    def draw_image(self, path):
        for curve in path:
            self.draw_curve(curve)


    # draws a single curve
    def draw_curve(self, curve):
        start = curve.start_point
        for segment in curve:
            x0, y0 = ImageTracer.get_tuple(start) # remove once get tuple not needed
            if segment.is_corner:
                x1, y1 = ImageTracer.get_tuple(segment.c) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                # draw segment
            else:
                x1, y1 = ImageTracer.get_tuple(segment.c1) # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.c2) # remove once get tuple not needed
                x3, y3 = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed
                # draw segment
            start = ImageTracer.get_tuple(segment.end_point) # remove once get tuple not needed


    # moves robot to new position from current position
    # returns new position to update current_pos
    def go_to_position(self, x_cur, y_cur, x_new, y_new):
        # move position
        return x_new, y_new


    # returns x position on a segment given points from the equation and time 0 <= t <= 1
    # corner segments are broken into 2 parts
    # x0, x1 and
    # x1, x2
    # if working on the x1, x2 part use those as parameters for x0, x1 respectively
    def get_x_position(self, t, x0, x1, x2=-1, x3=-1):
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
    def get_y_position(self, t, y0, y1, y2=-1, y3=-1):
        if t < 0 or t > 1:
            raise ValueError("t value not between 0 and 1")
        if(y2==-1 and y3==-1):
            return (1 - t) * y0 + t * y1
        else:
            return (1 - t) * ((1 - t) * ((1 - t) * y0 + t * y1) + t * ((1 - t) * y1 + t * y2)) + t * (
                    (1 - t) * ((1 - t) * y1 + t * y2) + t * ((1 - t) * y2 + t * y3))


    # returns velocity between 2 x or y values
    # intended for velocity in 1 axis
    def get_velocity(self, p0, p1):
        return p1 - p0


    # test function for testing gui
    def draw_image_test(self, path):
        print("done")


if __name__ == "__main__":
    print("debug todo")
