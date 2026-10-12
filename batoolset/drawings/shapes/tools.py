from batoolset.settings.global_settings import set_UI  # set the UI to qtpy
set_UI()
from batoolset.lists.tools import flatten_list
from qtpy.QtCore import QPointF, QRectF, QRect, Qt, QLineF
from qtpy.QtGui import QPolygonF, QPainterPath, QBrush
from qtpy.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
import math
import sys


def subtract_polygons(polygon1, polygon2, return_path_instead_of_polygon=False):
    path1 = QPainterPath()
    path1.addPolygon(polygon1)

    path2 = QPainterPath()
    path2.addPolygon(polygon2)

    result_path = path1 - path2
    # result_path = path1.subtracted(path2)
    if return_path_instead_of_polygon:  # useful for an area of an intersection !!!
        return result_path

    result_polygon = result_path.toFillPolygon()

    return result_polygon


def union_of_polygons(polygon1: QPolygonF, polygon2: QPolygonF) -> QPolygonF:
    path1 = QPainterPath()
    path1.addPolygon(polygon1)

    path2 = QPainterPath()
    path2.addPolygon(polygon2)

    result_path = path1 + path2
    result_polygon = result_path.toFillPolygon()

    return result_polygon


def qpolygonf_to_list(qpolygonf, unpack=False):
    lst = [(point.x(), point.y()) for point in qpolygonf]
    if not unpack:
        return lst
    else:
        return flatten_list(lst)


def get_area_after_subtraction(qpolygonf1, qpolygonf2):
    from shapely.geometry import Polygon
    # Function to convert QPolygonF to a list of tuples

    # Convert QPolygonF to a list of tuples
    polygon1_list = qpolygonf_to_list(qpolygonf1)
    polygon2_list = qpolygonf_to_list(qpolygonf2)

    # Convert the list of tuples to shapely Polygon objects
    shapely_polygon1 = Polygon(polygon1_list)
    shapely_polygon2 = Polygon(polygon2_list)

    # Get the area of the resulting polygon after subtracting polygon2 from polygon1
    result_polygon = shapely_polygon1.difference(shapely_polygon2)
    result_area = result_polygon.area

    return result_area


# Function to convert QPolygonF to a list of tuples


def polygon_area(polygon: QPolygonF) -> float:
    area = 0.
    num_points = len(polygon)
    j = num_points - 1

    for i in range(num_points):
        point1 = polygon[i]
        point2 = polygon[j]
        area += (point2.x() + point1.x()) * (point2.y() - point1.y())
        j = i

    return abs(area) / 2.

    # area = 0.0
    # n = len(polygon)
    #
    # # Iterate through the vertices of the polygon
    # for i in range(n - 1):
    #     x1, y1 = polygon[i].x(), polygon[i].y()
    #     x2, y2 = polygon[i + 1].x(), polygon[i + 1].y()
    #     area += x1 * y2 - x2 * y1
    #
    # # Close the polygon by connecting the last vertex to the first one
    # x1, y1 = polygon[n - 1].x(), polygon[n - 1].y()
    # x2, y2 = polygon[0].x(), polygon[0].y()
    # area += x1 * y2 - x2 * y1
    #
    # # Take the absolute value to ensure the area is positive
    # area = abs(area / 2.0)

    # return polygon.area()


# def calculate_area(*polygons):
#     if not polygons:
#         return 0
#
#     path1 = QPainterPath()
#     path1.addPolygon(polygons[0])
#     path1 = path1.simplified()
#
#     for polygon in polygons[1:]:
#         path2 = QPainterPath()
#         path2.addPolygon(polygon)
#         path2 = path2.simplified()
#         path1 = path1.subtracted(path2)
#         path1 = path1.simplified()
#
#     total_area = 0
#     for subpath_polygon in path1.toSubpathPolygons():
#         area = polygon_area(subpath_polygon)
#         total_area += area
#
#     return total_area

# from shapely.geometry import Polygon
#
# def calculate_area(*polygons):
#     if not polygons:
#         return 0
#
#     polygon1 = Polygon(polygons[0])
#
#     for points in polygons[1:]:
#         polygon2 = Polygon(points)
#         polygon1 = polygon1.difference(polygon2)
#
#     if polygon1.is_empty:
#         return 0
#     else:
#         return polygon1.area
#
# # Example usage
# polygon1 = np.array([[10, 10], [100, 10], [100, 100], [10, 100]])
# polygon2 = np.array([[30, 30], [80, 30], [80, 80], [30, 80]])

def calculate_area(qpolygon):
    area = 0
    for i in range(qpolygon.size()):
        p1 = qpolygon[i]
        p2 = qpolygon[(i + 1) % qpolygon.size()]
        d = p1.x() * p2.y() - p2.x() * p1.y()
        area += d
    return abs(area) / 2


def intersect(polygon1, polygon2):
    return polygon1.intersected(polygon2)


def union(polygon1, polygon2):
    return polygon1.united(polygon2)


# all the area calculations are wrong

# result_area = calculate_area(polygon1, polygon2)
# print(f"Area of the resulting polygon: {result_area}")

# def polygon_to_closest_circle(polygon: QPolygonF) -> QPolygonF:
#     # Calculate the area of the polygon
#     area = calculate_area(polygon)
#
#     # Calculate the equivalent circle radius
#     radius = math.sqrt(area / math.pi)
#
#     # Create a QRectF object that represents the bounding rectangle of the circle
#     bounding_rect = QRectF(-radius, -radius, 2 * radius, 2 * radius)
#
#     # Create a QPainterPath object and add an ellipse (circle) to it
#     path = QPainterPath()
#     path.addEllipse(bounding_rect)
#
#     # Convert the QPainterPath object to a QPolygonF object
#     circle_polygon = path.toFillPolygon()
#
#     return circle_polygon
def get_radius_of_circle_corresponding_to_polygon(poly):
    area = calculate_area(poly)
    # Calculate the equivalent circle radius
    radius = math.sqrt(area / math.pi)
    # Calculate the diameter
    # diameter = 2. * radius

    return radius


def create_rect_centered_at(point, radius):
    rect = QRectF()
    rect.setLeft(point.x() - radius)
    rect.setTop(point.y() - radius)
    rect.setWidth(2 * radius)
    rect.setHeight(2 * radius)
    return rect


def rect_intersects_polygon(rect: QRectF, polygon: QPolygonF) -> bool:
    # Create a QPainterPath object for the QRectF
    rect_path = QPainterPath()
    rect_path.addRect(rect)

    # Create a QPainterPath object for the QPolygonF
    polygon_path = QPainterPath()
    polygon_path.addPolygon(polygon)

    # Check if the two paths intersect
    intersects = rect_path.intersects(polygon_path)

    return intersects


def perpendicular_distance(point: QPointF, line_start: QPointF, line_end: QPointF) -> float:
    dx = line_end.x() - line_start.x()
    dy = line_end.y() - line_start.y()

    # Normalize the vector
    magnitude = math.hypot(dx, dy)
    if magnitude > sys.float_info.epsilon:
        dx /= magnitude
        dy /= magnitude

    # Calculate the vector dot product
    pvx = point.x() - line_start.x()
    pvy = point.y() - line_start.y()
    dot_product = dx * pvx + dy * pvy

    # Calculate the perpendicular distance
    ax = line_start.x() + dot_product * dx
    ay = line_start.y() + dot_product * dy
    distance = math.hypot(point.x() - ax, point.y() - ay)

    return distance


# def simplify_polygon(polygon, tolerance):
#     if len(polygon) <= 2:
#         return polygon
#
#     markers = [False] * len(polygon)
#     markers[0] = markers[-1] = True
#
#     dists = [0.0] * len(polygon)
#     furthest_point_index = 0
#     furthest_distance = 0.0
#
#     line = QLineF(polygon[0], polygon[-1])
#     line_length = line.length()
#     for i in range(1, len(polygon) - 1):
#         point = polygon[i]
#         closest_point = line.closestPointWithinLine(point)
#         dist = closest_point.distanceToPoint(point)
#         dists[i] = dist
#         if dist > furthest_distance:
#             furthest_distance = dist
#             furthest_point_index = i
#
#     if furthest_distance > tolerance:
#         markers[furthest_point_index] = True
#         simplified_left = simplify_polygon([polygon[i] for i in range(furthest_point_index + 1)], tolerance)
#         simplified_right = simplify_polygon([polygon[i] for i in range(furthest_point_index, len(polygon))], tolerance)
#         simplified_polygon = simplified_left[:-1] + simplified_right
#     else:
#         simplified_polygon = [polygon[0], polygon[-1]]
#
#     return QPolygonF(simplified_polygon)

def simplify_polygon2(polygon: QPolygonF) -> QPolygonF:
    # # not tested --> TODO
    # if len(polygon) <= 2:
    #     return polygon
    #
    # # Find the point with the maximum distance from the line between the start and end points
    # max_distance = 0.0
    # index = 0
    # for i in range(1, len(polygon) - 1):
    #     distance = perpendicular_distance(polygon[i], polygon[0], polygon[-1])
    #     if distance > max_distance:
    #         max_distance = distance
    #         index = i
    #
    # # Check if the maximum distance is greater than the epsilon threshold
    # if max_distance > epsilon:
    #     # Recursively simplify the two sub-polygons
    #     first_half = simplify_polygon(polygon[:index + 1], epsilon)
    #     second_half = simplify_polygon(polygon[index:], epsilon)
    #
    #     # Combine the results and remove the duplicate point
    #     simplified_polygon = first_half[:-1] + second_half[1:]
    # else:
    #     # The polygon can be represented by a line between the start and end points
    #     simplified_polygon = QPolygonF([polygon[0], polygon[-1]])
    #
    # return simplified_polygon
    return polygon.simplified()


# def qrectf_qpolygonf_intersection(qrectf, qpolygonf):
#     rect_points = [(qrectf.left(), qrectf.top()),
#                    (qrectf.right(), qrectf.top()),
#                    (qrectf.right(), qrectf.bottom()),
#                    (qrectf.left(), qrectf.bottom())]
#
#     poly_points = [(point.x(), point.y()) for point in qpolygonf]
#
#     for point in rect_points:
#         if qpolygonf.containsPoint(QPointF(*point), 0):
#             return True
#
#     for point in poly_points:
#         if qrectf.contains(QPointF(*point)):
#             return True
#
#     return False
def get_polygon_union(*polygons):
    if not polygons:
        return QPolygonF()

    union_path = QPainterPath()
    union_path.addPolygon(polygons[0])

    for polygon in polygons[1:]:
        polygon_path = QPainterPath()
        polygon_path.addPolygon(polygon)
        union_path = union_path.united(polygon_path)

    return union_path.toFillPolygon()


def get_polygon_difference(polygons):  # this is the intersection
    if not polygons:
        # return QPolygonF()
        return None

    # Find the largest polygon
    largest_polygon = max(polygons, key=lambda p: p.boundingRect().width() * p.boundingRect().height())

    diff_path = QPainterPath()
    diff_path.addPolygon(largest_polygon)

    for polygon in polygons:
        if polygon != largest_polygon:
            polygon_path = QPainterPath()
            polygon_path.addPolygon(polygon)
            diff_path = diff_path.subtracted(polygon_path)

    return diff_path.toFillPolygon()


if __name__ == '__main__':
    if True:
        # try the fusion of

        sys.exit(0)

    app = QApplication([])

    polygon1 = QPolygonF([
        QPointF(10, 10),
        QPointF(100, 10),
        QPointF(100, 100),
        QPointF(10, 100)
    ])

    polygon2 = QPolygonF([
        QPointF(30, 30),
        QPointF(80, 30),
        QPointF(80, 80),
        QPointF(30, 80)
    ])

    # Create a complex polygon that roughly simplifies to polygon2
    complex_polygon = QPolygonF([
        QPointF(30, 30),
        QPointF(35, 33),
        QPointF(40, 32),
        QPointF(45, 35),
        QPointF(50, 30),
        QPointF(55, 32),
        QPointF(60, 35),
        QPointF(65, 28),
        QPointF(70, 33),
        QPointF(75, 29),
        QPointF(80, 30),

        QPointF(80, 80),
        QPointF(75, 78),
        QPointF(70, 82),
        QPointF(65, 80),
        QPointF(60, 85),
        QPointF(55, 82),
        QPointF(50, 80),
        QPointF(45, 83),
        QPointF(40, 79),
        QPointF(35, 81),
        QPointF(30, 80),

        QPointF(30, 30)  # Close the polygon by connecting the last point to the first point
    ])

    intersection = polygon1.united(polygon2)

    result_polygon = subtract_polygons(polygon1, polygon2)

    print(result_polygon)
    # print(result_polygon.points)

    # Calculate the area of the result_polygon
    # area = polygon_area(result_polygon)
    area = calculate_area(result_polygon)  # incorrect
    print(f"Area of the resulting polygon (incorrect): {area}")  # incorrect -−> USE THE ONE BELOW
    print(
        f"Area of the resulting polygon: {get_area_after_subtraction(polygon1, polygon2)}")  # now that works too bad i can't get it directly from the resulting polygon of the  subtraction

    # epsilon = 1.0  # The epsilon value controls the level of simplification (higher values result in more simplification)
    # simplified_polygon = simplify_polygon(complex_polygon, epsilon)
    # simplified_polygon = simplify_polygon(complex_polygon)
    # simplified_polygon = simplify_polygon(complex_polygon, 5) --> TODO reimplement my own java code because it was much better than that

    # Convert the polygon to the closest circle
    # circle_polygon = polygon_to_closest_circle(polygon1)
    # Calculate the area of the polygon
    # area = calculate_area(polygon1)
    # Calculate the equivalent circle radius
    radius = get_radius_of_circle_corresponding_to_polygon(polygon1)
    # Calculate the diameter
    diameter = 2. * radius
    print(f"Radius of the closest circle: {radius}")
    print(f"Diameter of the closest circle: {diameter}")

    # no way
    # area_result = calculate_area(polygon1, polygon2)
    # area_result = calculate_area(result_polygon)
    # print(f"Area of the resulting polygon: {area_result}")

    print(f"Area of the parent polygons: {polygon_area(polygon1)}, {polygon_area(polygon2)}")

    scene = QGraphicsScene()
    # polygon_item =scene.addPolygon(result_polygon)

    polygon_item = scene.addPolygon(intersection)

    scene.addPolygon(simplified_polygon)

    print(calculate_area(simplified_polygon))  # it does not work it is 0

    # scene.addPolygon(circle_polygon)

    if False:
        # Set a brush for the polygon_item to fill it with a specific color
        brush = QBrush(Qt.darkBlue)
        polygon_item.setBrush(brush)

    view = QGraphicsView(scene)
    view.setGeometry(QRect(0, 0, 400, 400))
    view.show()

    app.exec_()
