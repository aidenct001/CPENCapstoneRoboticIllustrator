import tkinter as tk
import numpy as np
import ImageTracer as it
from tkinter import filedialog
from tkinter import messagebox
from tkinter import font
from PIL import Image
from RobotControl import RobotControl


# test method
def select_image_test():
    array_test = np.zeros((32, 32), np.uint32)
    array_test[8:32 - 8, 8:32 - 8] = 255
    image_path = it.get_trace(array_test)
    # visual of array
    with open('./testimages/array.txt', 'w') as f:
        np.set_printoptions(threshold=np.inf)
        arraystring = np.array_str(array_test)
        f.write(arraystring)
    # equations
    equations = it.get_latex(image_path)
    with open('./testimages/equations.txt', 'w') as f:
        for equation in equations:
            f.write('{}\n'.format(equation))
    robot.load_path(image_path)


# Opens file browser to allow user to select file.
# Loads selected file into robot control
def select_image_from_file():
    if(robot.is_running()):
        messagebox.showerror("Robotic Illustrator", "Robot must be stoppped to change drawing")
        return
    image_file_path = filedialog.askopenfilename()
    if image_file_path == "":
        messagebox.showerror("Robotic Illustrator", "No file selected")
        return
    image = Image.open(image_file_path)
    contrast = 128
    image_path = it.get_trace(np.array(it.maximize_contrast(it.grayscale(image), contrast)))
    robot.load_path(image_path)
    messagebox.showinfo("Robotic Illustrator", "Image successfully loaded")


# Starts the robot
def start_drawing():
    if robot.is_loaded():
        if not robot.is_running():
            robot.start_drawing()
        else:
            messagebox.showerror("Robotic Illustrator", "Robot is already drawing")
            return
    else:
        messagebox.showerror("Robotic Illustrator", "Image file must be loaded to start drawing")


# Stops the robot
def stop_drawing():
    robot.stop_drawing()

if __name__ == "__main__":
    robot = RobotControl()
    window = tk.Tk()

    button_font = font.Font(size = 25)
    header_font = font.Font(size = 40, weight = "bold")

    header = tk.Label(window, text = "Robotic Illustrator", bg = "#222222", fg = "white", width = 1000, height = 3)
    header.pack(side = "top")
    header["font"] = header_font

    button_select = tk.Button(window, text = "Select Image", command = select_image_from_file, bg = "blue", fg = "white", width = 11)
    button_select.pack(side = "top", padx = 10, pady = 10)
    button_select["font"] = button_font

    button_start = tk.Button(window, text = "Start Drawing", command = start_drawing, bg = "green", width = 11)
    button_start.pack(side = "left", padx = 10, pady = 10)
    button_start["font"] = button_font

    button_stop = tk.Button(window, text = "Stop Drawing", command = stop_drawing, bg = "red", width = 11)
    button_stop.pack(side = "right", padx = 10, pady = 10)
    button_stop["font"] = button_font

    window.configure(bg = "#333333")
    window.title("Robotic Illustrator")
    window.geometry("600x400")

    window.mainloop()
