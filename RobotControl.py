import ImageTracer as it
import RPi.GPIO as GPIO
import threading
import math
import time
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo

# Constants
PEN_IS_UP = 0
PEN_IS_DOWN = 1
CW = 0
CCW = 1


class RobotControl:
    def __init__(self, path=None):
        self._current_x_pos = 0
        self._current_y_pos = 0
        self._path = path
        self._current_pen_pos = PEN_IS_UP
        self._steps_per_rev = 200  # (360/1.8)
        self._delay = 0.0009  # base delay
        # x-axis step and direction pins on rpi
        self._STEP1 = 8
        self._DIR1 = 10
        # y-axis step and direction pins on rpi
        self._STEP2 = 17
        self._DIR2 = 23
        # pin for pen servo motor
        self._factory = PiGPIOFactory()
        self._servo = Servo(13, pin_factory=self._factory)
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
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._DIR1, GPIO.OUT)
        GPIO.setup(self._STEP1, GPIO.OUT)
        GPIO.output(self._DIR1, CW)  # Default direction: clockwise
        # Setup for y-axis motor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._DIR2, GPIO.OUT)
        GPIO.setup(self._STEP2, GPIO.OUT)
        GPIO.output(self._DIR2, CW)  # Default direction: clockwise

    # draws every curve in an image
    def _draw_image(self):
        for curve in self._path:
            if not self._stop_event.is_set():
                self._draw_curve(curve)

    # draws a single curve
    def _draw_curve(self, curve):
        start = curve.start_point
        x0, y0 = it.get_tuple(start)
        self._go_to_position(x0, y0)
        self._pen_down()
        for segment in curve:
            if segment.is_corner:
                x1, y1 = it.get_tuple(segment.c)
                x2, y2 = it.get_tuple(segment.end_point)
                if not self._stop_event.is_set():
                    self._go_to_position(x1, y1)
                if not self._stop_event.is_set():
                    self._go_to_position(x2, y2)
            else:
                x1, y1 = it.get_tuple(segment.c1)
                x2, y2 = it.get_tuple(segment.c2)
                x3, y3 = it.get_tuple(segment.end_point)
                # for t in range(1, 11):
                #     t /= 10
                if not self._stop_event.is_set(): # no linear approximation
                    self._go_to_position(self._get_x_position(1, x0, x1, x2, x3),
                                        self._get_y_position(1, y0, y1, y2, y3))
            start = it.get_tuple(segment.end_point)
        self._pen_up()
        #self._reset_pen()
        self._running_event.clear()

    # resets pen to 0,0 from current postion
    def _reset_pen(self):
        self._go_to_position(0, 0)
        self._stop_event.clear()

    # moves pen down if not already down
    def _pen_down(self):
        if self._current_pen_pos == PEN_IS_DOWN:
            return
        self._servo.mid()
        time.sleep(1)
        self._servo.min() 
        time.sleep(1)
        self._current_pen_pos = PEN_IS_DOWN
        print("pen down")

    # moves pen up if not already up
    def _pen_up(self):
        if self._current_pen_pos == PEN_IS_UP:
            return
        self._servo.min()
        time.sleep(1)
        self._servo.mid() 
        time.sleep(1)
        self._current_pen_pos = PEN_IS_UP
        print("pen up")

    # moves robot to new position from current position
    # updates current_pos to new position
    def _go_to_position(self, x_new, y_new):
        print("moving from x={} y={} to x={} y={}".format(self._current_x_pos, self._current_y_pos, x_new, y_new))
        x_steps = math.floor(x_new - self._current_x_pos)
        y_steps = math.floor(y_new - self._current_y_pos)
        # Set motor direction for x-axis motor
        GPIO.output(self._DIR1, (CW if x_steps > 0 else CCW))
        # Set motor direction for y-axis motor
        GPIO.output(self._DIR2, (CW if y_steps > 0 else CCW))
        # Make abs after direction is set
        x_steps = abs(x_steps)
        y_steps = abs(y_steps)
        # set delay offset for diagonals
        x_delay = self._delay
        y_delay = self._delay
        if x_steps == 0 or y_steps == 0 or x_steps == y_steps:
            pass # straight line or 45 degree line, no change needed
        elif x_steps < y_steps:
            x_delay *= (y_steps / x_steps) # make x_delay longer due to less steps
        elif x_steps > y_steps:
            y_delay *= (x_steps / y_steps) # make y_delay longer due to less steps
        # motor movement
        thread_x = threading.Thread(target=self._move_x_motor, args = (x_steps, x_delay))
        thread_y = threading.Thread(target=self._move_y_motor, args = (y_steps, y_delay))
        thread_x.start()
        thread_y.start()
        thread_x.join()
        thread_y.join()
        # set to new position
        self._current_x_pos = x_new
        self._current_y_pos = y_new
        
    # moves y motor based on steps and variable delay
    def _move_x_motor(self, steps, delay):
        for step in range(steps):
            GPIO.output(self._STEP1, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self._STEP1, GPIO.LOW)
            time.sleep(delay)
    
    # moves y motor based on steps and variable delay
    def _move_y_motor(self, steps, delay):
        for step in range(steps):
            GPIO.output(self._STEP2, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(self._STEP2, GPIO.LOW)
            time.sleep(delay)

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
