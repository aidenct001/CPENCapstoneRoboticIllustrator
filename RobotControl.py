import ImageTracer


# draws every curve in an image
def draw_image(path):
    for curve in path:
        draw_curve(curve)


# draws a single curve
def draw_curve(curve):
    start = curve.start_point
    for segment in curve:
        x0, y0 = start
        if segment.is_corner:
            x1, y1 = segment.c
            x2, y2 = segment.end_point
            # draw segment
        else:
            x1, y1 = segment.c1
            x2, y2 = segment.c2
            x3, y3 = segment.end_point
            # draw segment
        start = segment.end_point


if __name__ == "__main__":
    print("debug todo")
