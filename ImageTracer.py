import numpy as np
from PIL import Image
import potrace
import os # rm when not needed


# variable terminology
# image = image object containing png or jpeg
# array = bitmap of pixels from an image
# path = all svg data from an image
# curve = single full shape from a path
# segment = single line from a curve


# returns a grayscale image
def grayscale(image, image_file_path_gray=None):
    temp_image = image.convert('L')
    if image_file_path_gray is not None: 
        temp_image.save(image_file_path_gray)
    return temp_image


# returns a black and white image
def maximize_contrast(image, contrast_amount=128, image_file_path_black=None):
    temp_image = image.point(lambda x: 0 if x < contrast_amount else 255)
    if image_file_path_black is not None: 
        temp_image.save(image_file_path_black)
    # os check windows needs 255 and linux needs 1 for their respective potrace implementations. change after ui dev | rm when not needed
    return image.point(lambda x: 0 if x < contrast_amount else (lambda osname: 255 if osname == "nt" else 1)(os.name))


# returns a path from a bitmap data
def get_trace(array):
    return potrace.Bitmap(array).trace()


# returns tuple data if corner is a point object
# remove when not needed
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
            x0, y0 = get_tuple(start) # remove once get tuple not needed
            if segment.is_corner:
                x1, y1 = get_tuple(segment.c) # remove once get tuple not needed
                x2, y2 = get_tuple(segment.end_point) # remove once get tuple not needed
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x0, x1, y0, y1))
                latex.append('((1-t){}+t{},(1-t){}+t{})'.format(x1, x2, y1, y2))
            else:
                x1, y1 = get_tuple(segment.c1) # remove once get tuple not needed
                x2, y2 = get_tuple(segment.c2) # remove once get tuple not needed
                x3, y3 = get_tuple(segment.end_point) # remove once get tuple not needed
                latex.append('((1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})),\
                (1-t)((1-t)((1-t){}+t{})+t((1-t){}+t{}))+t((1-t)((1-t){}+t{})+t((1-t){}+t{})))'.format
                             (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = get_tuple(segment.end_point) # remove once get tuple not needed
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
    face_image_file_path = "./testimages/face.JPG"
    face_image_file_path_gray = "./testimages/faceg.png"
    face_image_file_path_black = "./testimages/faceb.png"
    # TEST METHODS
    # get "svg"
    # change test image here
    # image_path = get_trace(image1)
    contrast = 128
    car_image_path = get_trace(np.array(maximize_contrast(grayscale(Image.open(car_image_file_path), car_image_file_path_gray), contrast, car_image_file_path_black)))
    # too slow on windows
    # face_image_path = get_trace(get_array(maximize_contrast(grayscale(get_image(face_image_file_path), face_image_file_path_gray), contrast, face_image_file_path_black)))
    # send equations to file
    equations = get_latex(car_image_path)
    with open('./testimages/equations.txt', 'w') as f:
        for equation in equations:
            f.write('{}\n'.format(equation))
