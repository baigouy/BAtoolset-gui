from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from batoolset.drawings.shapes.freehand2d import Freehand2D
from batoolset.drawings.shapes.polyline2d import PolyLine2D
from batoolset.serializations.tools import clone_object
from qtpy.QtCore import QRectF, QPointF,QPoint
from qtpy.QtGui import QTransform, QPolygonF,QPolygon
import numpy as np
from batoolset.drawings.shapes import polyline2d, freehand2d
from batoolset.drawings.shapes.ellipse2d import Ellipse2D
from batoolset.drawings.shapes.line2d import Line2D
from batoolset.drawings.shapes.point2d import Point2D
from batoolset.drawings.shapes.polygon2d import Polygon2D
from batoolset.drawings.shapes.rectangle2d import Rectangle2D


def translated(shape, point):
    # get the rotated

    # if not centroid:
    centroid = get_centroid(get_points(shape))

    if isinstance(centroid, (QPointF, QPoint)):
        centroid = (centroid.x(), centroid.y())

    # new_centoid=
    transform = Transform2D()
    transform.translate(point[0], point[1])

    print(centroid)

    centroid = transform.apply(centroid)

    print('after', centroid)

    # then see how to return the modified shape
    # whatever the shape I need to center it to some position
    # and to clone it

    clone = clone_object(shape)
    # clone.theta = clone.theta+angle
    # then I need to center the stuff
    clone.set_to_center(centroid)

    # in some cases I may need to do more crazy stuff

    return clone

def rotated(shape, angle, centroid=None):
    # get the rotated

    if not centroid:
        centroid = get_centroid(get_points(shape))

    if isinstance(centroid, (QPointF, QPoint)):
        centroid = (centroid.x(), centroid.y())

    # new_centoid=
    transform = Transform2D()
    transform.translate(centroid[0], centroid[1])
    transform.rotate(angle)
    transform.translate(-centroid[0], -centroid[1])

    centroid = transform.apply(centroid)
    # then see how to return the modified shape
    # whatever the shape I need to center it to some position
    # and to clone it

    clone = clone_object(shape)
    clone.theta = clone.theta+angle
    # then I need to center the stuff
    clone.set_to_center(centroid)

    # in some cases I may need to do more crazy stuff

    return clone

def get_centroid(points):
    """Calculate the centroid of a list of 2D points.

    Args:
    points (list of tuple): List of (x, y) points.

    Returns:
    tuple: The (x, y) coordinates of the centroid.
    """
    if not points:
        raise ValueError("The list of points is empty.")

    try:
        x_coords = [p[0] for p in points]
        y_coords = [p[1] for p in points]
    except Exception:
        x_coords = [p.x() for p in points]
        y_coords = [p.y() for p in points]

    centroid_x = sum(x_coords) / len(points)
    centroid_y = sum(y_coords) / len(points)

    return centroid_x, centroid_y

def get_points(shape):

    # TODO --> I could do that for all shapes
    if isinstance(shape, QRectF):
        """Get the corners/vertices of a QRectF.

        Args:
        rect (QRectF): The rectangle from which to get the corners.

        Returns:
        list of tuple: A list containing the corners (x, y).
        """
        top_left = (shape.topLeft().x(), shape.topLeft().y())
        top_right = (shape.topRight().x(), shape.topRight().y())
        bottom_left = (shape.bottomLeft().x(), shape.bottomLeft().y())
        bottom_right = (shape.bottomRight().x(), shape.bottomRight().y())

        return [top_left, top_right, bottom_left, bottom_right]
    elif isinstance(shape, (QPolygon, QPolygonF, Polygon2D, PolyLine2D, Freehand2D)):
        # print('entering')
        vertices = []
        for point in shape:
            vertices.append((point.x(), point.y()))
        if shape.first() == shape.last(): # if poly is closed --> remove the point
            vertices=vertices[:-1]
        return vertices
    elif isinstance(shape,Point2D):
        return [(shape.x(), shape.y())]
    elif isinstance(shape,Line2D):
        return [((shape.x1()+shape.x2())/2., (shape.y1()+shape.y2())/2.)]
    elif isinstance(shape,Rectangle2D):
        return [shape.top_left(), shape.top_right(), shape.bottom_left(), shape.bottom_right()]
    elif isinstance(shape, Line2D):
        return [(shape.x1(), shape.y1()), (shape.x2(), shape.y2())]
    elif isinstance(shape, Line2D):
        return [(shape.x1(), shape.y1()), (shape.x2(), shape.y2())]
    # elif isinstance(shape, Ellipse2D): # probably need the rect
    #

def get_bounding_rect(points, return_qrectf=False):
    """Get the bounding rectangle of a list of 2D points.

    Args:
    points (list of tuple): List of (x, y) points.

    Returns:
    tuple: (min_x, min_y, max_x, max_y) representing the bounding rectangle.
    """
    if not points:
        raise ValueError("The list of points is empty.")

    # Initialize the min and max values with the first point
    min_x, min_y = points[0]
    max_x, max_y = points[0]

    # Iterate over all points to find the min and max x and y values
    for (x, y) in points:
        if x < min_x:
            min_x = x
        if x > max_x:
            max_x = x
        if y < min_y:
            min_y = y
        if y > max_y:
            max_y = y
    if return_qrectf:
        return QRectF(min_x, min_y, max_x-min_x, max_y-min_y)
    return min_x, min_y, max_x, max_y


class Transform2D:
    def __init__(self):
        # Initialize with the identity matrix
        self.matrix = np.identity(3)

    def translate(self, tx, ty):
        """Apply a translation by (tx, ty)."""
        translation_matrix = np.array([
            [1, 0, tx],
            [0, 1, ty],
            [0, 0, 1]
        ])
        self.matrix = np.dot(self.matrix, translation_matrix)
        return self

    def rotate(self, theta):
        """Apply a rotation by theta degrees."""
        radians = np.radians(theta)
        cos_theta = np.cos(radians)
        sin_theta = np.sin(radians)
        rotation_matrix = np.array([
            [cos_theta, -sin_theta, 0],
            [sin_theta, cos_theta, 0],
            [0, 0, 1]
        ])
        self.matrix = np.dot(self.matrix, rotation_matrix)
        return self

    def scale(self, sx, sy):
        """Apply scaling by (sx, sy)."""
        scale_matrix = np.array([
            [sx, 0, 0],
            [0, sy, 0],
            [0, 0, 1]
        ])
        self.matrix = np.dot(self.matrix, scale_matrix)
        return self

    def apply(self, points, auto_unpack_if_single=True):
        """Apply the transformation to a list of 2D points."""
        if isinstance(points, tuple):
            points=[points]
        transformed_points = []
        for point in points:
            x, y = point
            # Homogeneous coordinate vector
            point_matrix = np.array([x, y, 1])
            transformed_point = np.dot(self.matrix, point_matrix)
            transformed_points.append((transformed_point[0], transformed_point[1]))
        if auto_unpack_if_single and len(transformed_points)==1:
            return transformed_points[0]
        return transformed_points

    def reset(self):
        """Reset the transformation matrix to the identity matrix."""
        self.matrix = np.identity(3)
        return self

    def get_matrix(self):
        """Get the current transformation matrix."""
        return self.matrix





if __name__ == '__main__':


    # Example usage
    transform = Transform2D()
    transform.translate(2, 3).rotate(45).scale(2, 2)
    points = [(1, 1), (2, 2), (3, 3)]
    transformed_points = transform.apply(points)
    print("Transformed Points:", transformed_points)
    print("Transformation Matrix:\n", transform.get_matrix())


    transform = Transform2D()
    transform.translate(-10,10).translate(10,-10)
    print(transform.apply(points)) # does not work
    print("Transformation Matrix:\n", transform.get_matrix())

    # now implement that for squares and other shapes --> TODO
    # very good that works
    transform = Transform2D()
    transform.translate(0, 0).translate(1,-1)
    print(transform.apply(points))  # does not work
    print("Transformation Matrix:\n", transform.get_matrix())

    # points = [(10,20), (200+10,300+20), (210,20), (10, 320)]
    rect = QRectF(10,20,200, 300)
    points = get_points(rect)
    print('points',points)
    print('get_centroid',get_centroid(points))
    center = rect.center()
    points.append((center.x(),center.y()))

    print(center)
    transform = Transform2D()
    transform.translate(center.x(),center.y())
    transform.rotate(45)
    transform.translate(-center.x(),-center.y())

    print(transform.apply(points))


    qtrafo = QTransform()
    qtrafo.translate(center.x(), center.y())
    qtrafo.rotate(45)
    qtrafo.translate(-center.x(), -center.y())

    print(qtrafo.map(10,20))
    print(qtrafo.map(210,320))
    print(qtrafo.map(center.x(),center.y()))

    # Example usage
    # points = [(1, 1), (2, 2), (3, 3), (-1, -1), (4, 0)]
    bounding_rect = get_bounding_rect(points)
    print("Bounding Rectangle:", bounding_rect)

    # is that really correct --> looks like there is a bug!!!

    print(get_bounding_rect(transform.apply(points)))
    print(qtrafo.mapRect(rect)) # la sortie est pas du tout la meme


    print(get_bounding_rect(transform.apply(points), return_qrectf=True)) # no it's ok but I really need the four corner to get the real bounding rect
    # and then that works perfectly

    polygon = QPolygonF([QPointF(0, 0), QPointF(1, 1), QPointF(2, 0), QPointF(1, -1)])
    print(polygon.isClosed())
    vertices = get_points(polygon)
    print(vertices)
    if polygon.first() != polygon.last():
        polygon.append(polygon.first())
    vertices = get_points(polygon)
    print(vertices)

    # what is map rect doing in fact
    # the map rect seems to work though

    vertices2 = []
    for vx in vertices:
        vertices2.append(vx[0])
        vertices2.append(vx[1])
    print(len(vertices2))
    # poly = Polygon2D(*vertices2)
    p2d = Polygon2D(*vertices)

    print(get_points(p2d))


    print('p2d rot',rotated(p2d, 45).listVertices()) # pb is that it creates super minor rounding errors but maybe still ok!!!
    print('p2d rot',rotated(p2d, 45,(256,256)).listVertices()) # pb is that it creates super minor rounding errors but maybe still ok!!!


    # maybe that works
    # just try it maybe

    r2d = Rectangle2D(0,0,256,516)
    print('rect rot',rotated(r2d, 90).boundingRect())
    print('rect rot',rotated(r2d, 90,(256,256)).boundingRect())

    print('dab', r2d.x(), r2d.y(), r2d.width(), r2d.height())


    print(r2d.boundingRect().center(), 'vs',get_centroid(get_points(r2d)), get_points(r2d))
    trans = translated(r2d,(10,25))
    print('dab',trans.x(),trans.y(), trans.width(), trans.height(), trans.boundingRect())
    # --> à tester --> mais peut etre ok --> dessiner ttes les shapes tournées dans le truc # see if I can chain things or not ???

    # bug

    el2d = Ellipse2D(0,0,256,512)
    trans =translated(r2d, (10, 25))
    print(trans.x(),trans.y(), trans.width(), trans.height()) # --> ok it seems

    # TODO --> maybe try all for real now