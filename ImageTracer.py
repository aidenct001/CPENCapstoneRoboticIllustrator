import numpy as np
from PIL import Image
import potrace
import os


# variable terminology
# data = bitmap of pixels from an image
# path = all svg data from an image
# curve = single full shape from a path
# segment = single line from a curve


# returns an image object from an image file path
def get_image(file_path):
    return Image.open(file_path)


# returns a grayscale image
def grayscale(image):
    temp = image.convert('L')
    temp.save("./testimages/carg.png")
    return temp


# returns a black and white image
def maximize_contrast(image, c=128):
    temp = image.point(lambda x: 0 if x < c else 255)
    temp.save("./testimages/carb.png")
    # os check windows needs 255 and linux needs 1 for their respective potrace implementations
    return image.point(lambda x: 0 if x < c else (lambda o: 255 if o == "nt" else 1)(os.name))


# returns a numpy array from an image object
def get_data(image):
    return np.array(image)


# returns a path from a bitmap data
def get_trace(data):
    bmp = potrace.Bitmap(data)
    path = bmp.trace()
    return path


# combines the above functions
# returns an image path from a file path
def get_path_from_image(file_path):
    return get_trace(get_data(maximize_contrast(grayscale(get_image(file_path)))))


# returns tuple data if corner is a point object
def get_tuple(corner):
    if isinstance(corner, tuple):
        return corner
    else:
        return corner.x, corner.y


# DEBUG METHODS_________________________________________________________________________________________________________

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


# returns start, corner(s), and endpoints as an array of strings
# best for reading
def get_points(path):
    point_strings = []
    for curve in path:
        start = curve.start_point
        for segment in curve:
            point_strings.append("start_point = {} {}".format(start, segment))
            start = segment.end_point
    return point_strings


if __name__ == "__main__":

    # TEST DATA ________________________________________________________________________________________________________
    # large square filled (16x16)
    image1 = np.zeros((32, 32), np.uint32)
    image1[8:32 - 8, 8:32 - 8] = 1
    # rhombus
    image2 = np.matrix(
        [[0, 0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 1, 0],
         [0, 0, 1, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0]])
    # square not filled (7x7)
    image3 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]])
    # square filled (7x7)
    image4 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]])
    image_file_path = "./testimages/car.png"
    # __________________________________________________________________________________________________________________

    # TEST METHODS _____________________________________________________________________________________________________
    # get "svg"
    # change test image here
    # image_path = get_trace(image1)
    image_path = get_path_from_image(image_file_path)

    # print points on each curve
    # points = get_points(image_path)
    # for point in points:
    #     print(point)

    # print equations
    equations = get_latex(image_path)
    with open('equations.txt', 'w') as f:
        for equation in equations:
            f.write('{}\n'.format(equation))
    # __________________________________________________________________________________________________________________
