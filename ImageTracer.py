import numpy as np
import potrace
# variable terminology
# data = bitmap of pixels from an image
# path = all svg data from an image
# curve = single full shape from a path
# segment = single line from a curve


# returns a path from a bitmap data
def get_trace(data):
    bmp = potrace.Bitmap(data)
    path = bmp.trace()
    return path


# returns Bézier curves from the image path as an array of strings
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


# Prints start, corner(s), and endpoints
def get_points(path):
    point_strings = []
    for curve in path:
        start = curve.start_point
        for segment in curve:
            point_strings.append("start_point = {} {}".format(start, segment))
            start = segment.end_point
    return point_strings


if __name__ == "__main__":

    # TEST DATA ____________________________________________________________________________________
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
    # ______________________________________________________________________________________________

    # get "svg"
    image_path = get_trace(image4)
    # print points on each curve
    points = get_points(image_path)
    for point in points:
        print(point)
    # print equations for graphing
    equations = get_latex(image_path)
    for equation in equations:
        print(equation)
