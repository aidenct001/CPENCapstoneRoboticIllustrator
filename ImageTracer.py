import numpy as np
from PIL import Image
import potrace
import os


# variable terminology
# image: image object containing png or jpeg
# array = bitmap of pixels from an image
# path = all svg data from an image
# curve = single full shape from a path
# segment = single line from a curve


# returns an image object from an image file path
def get_image(image_file_path):
    return Image.open(image_file_path)


# returns a grayscale image
def grayscale(image, image_file_path_gray=None):
    temp = image.convert('L')
    if image_file_path_gray is not None: 
        temp.save(image_file_path_gray)
    return temp


# returns a black and white image
def maximize_contrast(image, contrast_amount=128, image_file_path_black=None):
    temp = image.point(lambda x: 0 if x < contrast_amount else 255)
    if image_file_path_black is not None: 
        temp.save(image_file_path_black)
    # os check windows needs 255 and linux needs 1 for their respective potrace implementations
    return image.point(lambda x: 0 if x < contrast_amount else (lambda osname: 255 if osname == "nt" else 1)(os.name))


# returns a numpy array from an image object
def get_array(image):
    return np.array(image)


# returns a path from a bitmap data
def get_trace(array):
    bmp = potrace.Bitmap(array)
    path = bmp.trace()
    return path


# returns tuple data if corner is a point object
def get_tuple(corner):
    if isinstance(corner, tuple):
        return corner
    else:
        return corner.x, corner.y


# DEBUG METHOD

# returns Bézier curves from the image path as an array of strings
# best for graphing
def get_latex(path):
    latex = []
    for curve in path:
        start = curve.start_point
        for segment in curve:
            x0, y0 = get_tuple(start)
            if segment.is_corner:
                x1, y1 = get_tuple(segment.c)
                x2, y2 = get_tuple(segment.end_point)
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x0, x1, y0, y1))
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x1, x2, y1, y2))
            else:
                x1, y1 = get_tuple(segment.c1)
                x2, y2 = get_tuple(segment.c2)
                x3, y3 = get_tuple(segment.end_point)
                latex.append('((1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})),\
                (1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})))'.format
                             (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = get_tuple(segment.end_point)
    return latex


if __name__ == "__main__":

    # TEST DATA 
    # large square filled (16x16)
    array1 = np.zeros((32, 32), np.uint32)
    array1[8:32 - 8, 8:32 - 8] = 1
    # rhombus
    array2 = np.matrix(
        [[0, 0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 1, 0],
         [0, 0, 1, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0]])
    # square not filled (7x7)
    array3 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]])
    # square filled (7x7)
    array4 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]])
    car_image_file_path = "./testimages/car.png"
    car_image_file_path_gray = "./testimages/carg.png"
    car_image_file_path_black = "./testimages/carb.png"

    # TEST METHODS
    # get "svg"
    # change test image here
    # image_path = get_trace(image1)
    contrast = 128
    image_path = get_trace(get_array(maximize_contrast(grayscale(get_image(car_image_file_path), car_image_file_path_gray), contrast, car_image_file_path_black)))

    # send equations to file
    equations = get_latex(image_path)
    with open('equations.txt', 'w') as f:
        for equation in equations:
            f.write('{}\n'.format(equation))
