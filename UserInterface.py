import tkinter as tk
import ImageTracer
from RobotControl import robot_control
import numpy as np # testing only


def select_image():
    return


def start_drawing():
    robot.start_drawing()


def stop_drawing():
    robot.stop_drawing()

if __name__ == "__main__":
    # square filled (7x7)
    array1 = np.zeros((32, 32), np.uint32)
    array1[8:32 - 8, 8:32 - 8] = 1
    image_path = ImageTracer.get_trace(array1)
    robot = robot_control(image_path)


    root = tk.Tk()
    button1 = tk.Button(root, text="Select Image", command=select_image)
    button1.pack()
    button2 = tk.Button(root, text="Start Drawing", command=start_drawing)
    button2.pack()
    button3 = tk.Button(root, text="Stop Drawing", command=stop_drawing)
    button3.pack()

    root.mainloop()

