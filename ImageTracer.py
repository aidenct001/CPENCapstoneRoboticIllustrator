import numpy as np
import potrace


def get_trace(data):
    # not sure what this is, probs for cv2 implementation
    # for i in range(len(data)):
    #     data[i][data[i] > 1] = 1
    bmp = potrace.Bitmap(data)
    path = bmp.trace()  # 2, potrace.TURNPOLICY_MINORITY, 1.0, 1, .5
    return path


def get_latex(path):
    latex = []
    for curve in path:
        start = curve.start_point
        for segment in curve:
            x0, y0 = start
            if segment.is_corner:
                x1, y1 = segment.c
                x2, y2 = segment.end_point
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x0, x1, y0, y1))
                latex.append('((1-t)%f+t%f,(1-t)%f+t%f)' % (x1, x2, y1, y2))
            else:
                x1, y1 = segment.c1
                x2, y2 = segment.c2
                x3, y3 = segment.end_point
                latex.append('((1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)),\
                (1-t)((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f))+t((1-t)((1-t)%f+t%f)+t((1-t)%f+t%f)))' %
                             (x0, x1, x1, x2, x1, x2, x2, x3, y0, y1, y1, y2, y1, y2, y2, y3))
            start = segment.end_point
    return latex


# not really needed
def print_curves(path):
    for curve in path:
        start = curve.start_point
        for segment in curve:
            print("start_point =", start, segment)
            start = segment.end_point


if __name__ == "__main__":
    # square
    data = np.zeros((32, 32), np.uint32)
    data[8:32 - 8, 8:32 - 8] = 1
    # rhombus
    data2 = np.matrix(
        [[0, 0, 0, 1, 0, 0, 0], [0, 0, 1, 0, 1, 0, 0], [0, 1, 0, 0, 0, 1, 0], [1, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 1, 0],
         [0, 0, 1, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0, 0]])
    # square not filled
    data3 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1], [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1],
         [1, 0, 0, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1]])
    # square filled
    data4 = np.matrix(
        [[1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1],
         [1, 1, 1, 1, 1, 1, 1], [1, 1, 1, 1, 1, 1, 1]])
    path = get_trace(data4)
    print_curves(path)
    equations = get_latex(path)
    for equation in equations:
        print(equation)
