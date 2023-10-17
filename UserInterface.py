import tkinter as tk
from tkinter import filedialog
import ImageTracer as it
from RobotControl import RobotControl
from RobotControl import RunningException
import numpy as np # testing only rm later


# test method
def select_image_test():
    array1 = np.zeros((32, 32), np.uint32)
    array1[8:32 - 8, 8:32 - 8] = 1
    image_path = it.get_trace(array1)
    robot.load_path(image_path)


# Opens file browser to allow user to select file.
# Loads selected file into robot control
def select_image_from_file():
    if(robot.is_running()):
        print("must be stoppped to change drawing") # change later for better gui message
        return
    image_file_path = filedialog.askopenfilename()
    if image_file_path == "":
        return
    contrast = 128
    image_path = it.get_trace(it.get_array(it.maximize_contrast(it.grayscale(it.get_image(image_file_path)), contrast)))
    robot.load_path(image_path)
    print("loaded image") # change later for better gui message


# Starts the robot
def start_drawing():
    if robot.is_loaded():
        if not robot.is_running():
            robot.start_drawing()
        else:
            print("already drawing") # change later for better gui message
            return
    else:
        print("not loaded") # change later for better gui message


# Stops the robot
def stop_drawing():
    robot.stop_drawing()

if __name__ == "__main__":
    robot = RobotControl()
    root = tk.Tk()
    button1 = tk.Button(root, text="Select Image", command=select_image_from_file)
    button1.pack()
    button2 = tk.Button(root, text="Start Drawing", command=start_drawing)
    button2.pack()
    button3 = tk.Button(root, text="Stop Drawing", command=stop_drawing)
    button3.pack()

    root.mainloop()
