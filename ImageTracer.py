import numpy as np
from PIL import Image
import potrace


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
    return image.convert('L')


# returns a black and white image
def maximize_contrast(image):
    return image.point(lambda x: 0 if x < 128 else 1)


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


# returns x position on a segment given points from the equation and time 0 <= t <= 1
# corner segments are broken into 2 parts
# x0, x1 and
# x1, x2
# if working on the x1, x2 part use those as parameters for x0, x1 respectively
def get_x_position(is_corner, t, x0, x1, x2=-1, x3=-1):
    if t < 0 or t > 1:
        raise ValueError("t value not between 0 and 1")
    if is_corner:
        return (1 - t) * x0 + t * x1
    else:
        return (1 - t) * ((1 - t) * ((1 - t) * x0 + t * x1) + t * ((1 - t) * x1 + t * x2)) + t * (
                (1 - t) * ((1 - t) * x1 + t * x2) + t * ((1 - t) * x2 + t * x3))


# returns y position on a segment given points from the equation and time 0 <= t <= 1
# corner segments are broken into 2 parts
# y0, y1 and
# y1, y2
# if working on the y1, y2 part use those as parameters for y0, y1 respectively
def get_y_position(is_corner, t, y0, y1, y2=-1, y3=-1):
    if t < 0 or t > 1:
        raise ValueError("t value not between 0 and 1")
    if is_corner:
        return (1 - t) * y0 + t * y1
    else:
        return (1 - t) * ((1 - t) * ((1 - t) * y0 + t * y1) + t * ((1 - t) * y1 + t * y2)) + t * (
                (1 - t) * ((1 - t) * y1 + t * y2) + t * ((1 - t) * y2 + t * y3))


# returns velocity between 2 x or y values
# intended for velocity in 1 axis
def get_velocity(p0, p1):
    return p1 - p0


# DEBUG METHODS_________________________________________________________________________________________________________

# returns Bézier curves from the image path as an array of strings
# best for graphing
def get_latex(path):
    latex = []
    for curve in path:
        start = curve.start_point
        for segment in curve:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x0, x1, y0, y1))
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x1, x2, y1, y2))
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                latex.append('((1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})),\
                (1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})))'.format
                             (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = segment.end_point
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

    # # print equations
    equations = get_latex(image_path)
    for equation in equations:
        print(equation)

    # testing position functions
    # for image_curve in image_path:
    #     istart = image_curve.start_point
    #     for image_segment in image_curve:
    #         ix0, iy0 = istart
    #         if image_segment.is_corner:
    #             ix1, iy1 = image_segment.c
    #             ix2, iy2 = image_segment.end_point
    #             print("first part of corner")
    #             print(get_x_position(True, .5, ix0, ix1))
    #             print(get_velocity(ix0, ix1))
    #             print(get_y_position(True, .5, iy0, iy1))
    #             print(get_velocity(iy0, iy1))
    #             print("second part of corner")
    #             print(get_x_position(True, .5, ix1, ix2))
    #             print(get_velocity(ix1, ix2))
    #             print(get_y_position(True, .5, iy1, iy2))
    #             print(get_velocity(iy1, iy2))
    #         else:
    #             ix1, iy1 = image_segment.c1
    #             ix2, iy2 = image_segment.c2
    #             ix3, iy3 = image_segment.end_point
    #             print(get_x_position(False, .5, ix0, ix1, ix2, ix3))
    #             # print(get_x_velocity(False, .5, ix0, ix1, ix2, ix3))
    #             print(get_y_position(False, .5, iy0, iy1, iy2, iy3))
    #         istart = image_segment.end_point
    # __________________________________________________________________________________________________________________
