import ImageTracer  # remove once get tuple not needed
# import RPi.GPIO as GPIO # leave commented out unless on RPi
import threading
import math
import time  # maybe not needed | for testing currently

# Constants
PEN_IS_UP = 0
PEN_IS_DOWN = 1


class RobotControl:
    def __init__(self, path=None):
        self._current_x_pos = 0
        self._current_y_pos = 0
        self._path = path
        self._current_pen_pos = PEN_IS_UP
        self._steps_per_rev = 200  # (360/1.8)
        self._delay = 0.005  # 1/200
        # x-axis step and direction pins on rpi
        self._STEP1 = 15
        self._DIR1 = 14
        # y-axis step and direction pins on rpi
        self._STEP2 = 23
        self._DIR2 = 24
        # z-axis step and direction pins on rpi
        self._STEP3 = 5
        self._DIR3 = 6
        self._stop_event = threading.Event()
        self._running_event = threading.Event()
        self._thread = None
        self._gpio_setup()

    # Starts the robot
    def start_drawing(self):
        self._running_event.set()
        self._thread = threading.Thread(target=self._draw_image)
        if self._stop_event.is_set:
            self._stop_event.clear()
        self._thread.start()

    # Interrupts the drawing with a clean exit
    def stop_drawing(self):
        self._stop_event.set()

    # Loads a new path object
    def load_path(self, path):
        self._path = path

    # Checks if path has been loaded by user
    def is_loaded(self):
        return False if self._path is None else True

    # checks if path has been loaded by user
    def is_running(self):
        return self._running_event.is_set()

    # sets gpio default values
    def _gpio_setup(self):
        # Setup for x-axis motor
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._DIR1, GPIO.OUT)
        GPIO.setup(self._STEP1, GPIO.OUT)
        GPIO.output(self._DIR1, 0)  # Default direction: clockwise

        # Setup for y-axis motor
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._DIR2, GPIO.OUT)
        GPIO.setup(self._STEP2, GPIO.OUT)
        GPIO.output(self._DIR2, 0)  # Default direction: clockwise

        # Setup for z-axis motor
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._DIR3, GPIO.OUT)
        GPIO.setup(self._STEP3, GPIO.OUT)
        GPIO.output(self._DIR3, 0)  # Default direction: clockwise

    # draws every curve in an image
    def _draw_image(self):
        for curve in self._path:
            if not self._stop_event.is_set():
                self._draw_curve(curve)

    # draws a single curve
    def _draw_curve(self, curve):
        start = curve.start_point
        x0, y0 = ImageTracer.get_tuple(start)  # remove once get tuple not needed
        self._go_to_position(x0, y0)  # go to start of curve
        self._pen_down()
        for segment in curve:
            if segment.is_corner:
                x1, y1 = ImageTracer.get_tuple(segment.c)  # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.end_point)  # remove once get tuple not needed
                if not self._stop_event.is_set():
                    self._go_to_position(x1, y1)
                if not self._stop_event.is_set():
                    self._go_to_position(x2, y2)
            else:
                x1, y1 = ImageTracer.get_tuple(segment.c1)  # remove once get tuple not needed
                x2, y2 = ImageTracer.get_tuple(segment.c2)  # remove once get tuple not needed
                x3, y3 = ImageTracer.get_tuple(segment.end_point)  # remove once get tuple not needed

                # This needs to be in go to position based on where x,y is compared to x cur,y cur
                # Setting motor direction for x-axis motor
                # if x1 > x3:
                #     GPIO.output(self._DIR1, 0)
                # elif x3 > x1:
                #     GPIO.output(self._DIR1, 1)

                # Setting motor direction for y-axis motor
                # if y1 > y3:
                #     GPIO.output(self._DIR2, 0)
                # elif y3 > y1:
                #     GPIO.output(self._DIR2, 1)

                for t in range(1, 11):
                    t /= 10
                    if not self._stop_event.is_set():
                        self._go_to_position(self._get_x_position(t, x0, x1, x2, x3),
                                             self._get_y_position(t, y0, y1, y2, y3))
            start = ImageTracer.get_tuple(segment.end_point)  # remove once get tuple not needed
        self._pen_up()
        self._reset_pen()
        self._running_event.clear()

    # resets pen to 0,0 from current postion
    def _reset_pen(self):
        self._go_to_position(0, 0)
        self._stop_event.clear()

    # moves pen down if not already down
    def _pen_down(self):
        if self._current_pen_pos == PEN_IS_DOWN:
            return

        self._current_pen_pos = PEN_IS_DOWN
        GPIO.output(self._DIR3, 0)
        for steps in 5:
            GPIO.output(self._STEP3, GPIO.HIGH)
            time.sleep(self._delay)
            GPIO.output(self._STEP3, GPIO.LOW)
            time.sleep(self._delay)
        # motor
        self._current_pen_pos = PEN_IS_DOWN
        print("pen down")  # rm later

    # moves pen up if not already up
    def _pen_up(self):
        if self._current_pen_pos == PEN_IS_UP:
            return

        GPIO.output(self._DIR3, 1)
        for steps in 5:
            GPIO.output(self._STEP3, GPIO.HIGH)
            time.sleep(self._delay)
            GPIO.output(self._STEP3, GPIO.LOW)
            time.sleep(self._delay)
        # motor
        self._current_pen_pos = PEN_IS_UP
        print("pen up")  # rm later

    # moves robot to new position from current position
    # updates current_pos to new position
    def _go_to_position(self, x_new, y_new):
        print("moving from x={} y={} to x={} y={}".format(self._current_x_pos, self._current_y_pos, x_new, y_new)) # rm later

        # Linear Distance per step = (Pi * D) / (N * 360)
        # where D is the pitch of the lead screw (mm)
        # where N is the step angle (degrees)
        LinDistPerStep = (math.pi * 38) / (1.8 * 360)

        # Distance between pairs of coordinates
        CoordinateDist = math.sqrt((x_new - self._current_x_pos)**2 + ((y_new - self._current_y_pos)**2))

        # Number of steps for each axis motor to perform
        NumOfSteps = CoordinateDist / LinDistPerStep

        for step in NumOfSteps:
            GPIO.output(self._STEP1, GPIO.HIGH)
            time.sleep(self._delay)
            GPIO.output(self._STEP1, GPIO.LOW)
            time.sleep(self._delay)

            GPIO.output(self._STEP2, GPIO.HIGH)
            time.sleep(self._delay)
            GPIO.output(self._STEP2, GPIO.LOW)
            time.sleep(self._delay)
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
    def __init__(self, message=""):
        self.message = message

    def __str__(self):
        return self.message
