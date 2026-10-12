import math
import os
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from qtpy.QtCore import QPointF, QLineF, QRectF, QPoint, Qt
from qtpy.QtGui import QBrush, QPen, QColor, QTransform,QPainterPath
from math import sqrt

from batoolset.tools.logger import TA_logger

logger = TA_logger()


def arrowhead_polygon(tail, tip, head_length, head_half_width):
    """Triangle of an arrowhead whose point is EXACTLY *tip* (QPointF), aimed
    along tail->tip. The head is sized in drawing units (so it keeps a constant
    size on the page) and grows backwards from the tip, so the tip stays on the
    pointed feature whatever the panel scale. Returns (QPainterPath, base) where
    base is the centre of the head's back edge; None if tail == tip."""
    dx = tip.x() - tail.x()
    dy = tip.y() - tail.y()
    length = math.hypot(dx, dy)
    if length <= 0:
        return None
    ux = dx / length
    uy = dy / length
    base = QPointF(tip.x() - ux * head_length, tip.y() - uy * head_length)
    # normal to the shaft
    nx = -uy * head_half_width
    ny = ux * head_half_width
    path = QPainterPath()
    path.moveTo(tip)
    path.lineTo(QPointF(base.x() + nx, base.y() + ny))
    path.lineTo(QPointF(base.x() - nx, base.y() - ny))
    path.closeSubpath()
    return path, base


def arrow_shaft(p1, p2, head_length, head_at_end, head_at_start):
    """The part of the line to stroke for an arrow: each end that carries a head
    is pulled back into that head (80 % of its length, where the head is still
    much wider than the line), so neither the line's end cap nor its width can
    poke past the tip. None if the heads swallow the whole line."""
    dx = p2.x() - p1.x()
    dy = p2.y() - p1.y()
    length = math.hypot(dx, dy)
    if length <= 0:
        return None
    ux = dx / length
    uy = dy / length
    inset = 0.8 * head_length
    start = inset if head_at_start else 0.
    end = length - (inset if head_at_end else 0.)
    if end <= start:
        return None
    return QLineF(QPointF(p1.x() + ux * start, p1.y() + uy * start),
                  QPointF(p1.x() + ux * end, p1.y() + uy * end))


class Line2D(QLineF):

    def __init__(self, *args, x1=0, y1=0, x2=0, y2=0, color=0xFFFFFF, opacity=1., stroke=0.65, arrow=False, line_style=None, theta=0,arrow_at_both_ends=False, arrowhead_width_scaler=4, arrowhead_height_scaler=12, __version__=1.0,**kwargs):
        if args:
            super(Line2D, self).__init__(*args)
        else:
            # x1pos: float, y1pos: float, x2pos: float, y2pos: float
            super(Line2D, self).__init__(x1,y1,x2,y2)


        # if not args:
        #     self.isSet = False
        # else:
        #     self.isSet = True
        self.color = color
        self.stroke = stroke
        self.opacity = opacity
        self.scale = 1
        # self.translation = QPointF()
        self.line_style = line_style
        # rotation
        self.theta = theta
        self.arrow = arrow
        self.arrow_at_both_ends = arrow_at_both_ends
        self.arrowhead_width_scaler =arrowhead_width_scaler
        self.arrowhead_height_scaler = arrowhead_height_scaler # in a way the booleans above could be replaced simply by setting that to non 0
        self.fill_color = None # by definition a line cannot be filled but that is useful to implement it to have an object that is compatible with the other shapes
        self.__version__ = __version__

    def set_rotation(self, theta):
        self.theta = theta

    def set_opacity(self, opacity):
        self.opacity = opacity

    def set_line_style(self,style):
        """
        allows lines to be dashed or dotted or have custom pattern

        :param style: a list of numbers or any of the following Qt.SolidLine, Qt.DashLine, Qt.DashDotLine, Qt.DotLine, Qt.DashDotDotLine but not Qt.CustomDashLine, Qt.CustomDashLine is assumed by default if a list is passed in. None is also a valid value that resets the line --> assume plain line
        :return:
        """
        self.line_style = style
        # if style is a list then assume custom pattern otherwise apply solidline

    # shall I remove all of these scale stuff in there --> best is to redraw them anyway ???

    def draw(self, painter, draw=True, parent=None):
        # TODO --> MAYBE ADD A PARENT AND ALWAYS DRAW RELATIVE TO IT
        if self.color is None:
            return

        if draw:
            painter.save()
            # print('inside', self.scale)

            pen = QPen(QColor(self.color))
            if self.stroke is not None:
                pen.setWidthF(self.stroke)
            if self.line_style is not None:
                if self.line_style in [Qt.SolidLine, Qt.DashLine, Qt.DashDotLine, Qt.DotLine, Qt.DashDotDotLine]:
                    pen.setStyle(self.line_style)
                elif isinstance(self.line_style, list):
                    pen.setStyle(Qt.CustomDashLine)
                    pen.setDashPattern(self.line_style)
            painter.setPen(pen)
            painter.setOpacity(self.opacity)
            # clone the line
            line_to_plot = self.translated(0, 0)

            if self.scale is not None and self.scale != 1: # probably I shall remove that as I will never use that outside!!!
                line_to_plot =self.__get_scaled_line(line_to_plot, self.scale)

            if parent is not None and parent.scale is not None and parent.scale != 1:
                line_to_plot =self.__get_scaled_line(line_to_plot, 1./parent.scale)

            if parent is not None:
                line_to_plot = line_to_plot.translated(parent.topLeft())

            # if self.translation is not None:
            #     line_to_plot.translate(self.translation)
            # print(line_to_plot)
            if self.theta is not None and self.theta != 0:
                painter.translate(line_to_plot.center())
                painter.rotate(self.theta)
                painter.translate(-line_to_plot.center())

            # print('line_to_plot',line_to_plot)


                # Reset the rotation of the painter object
                # painter.rotate(line_angle)

            if not self.arrow:
                painter.drawLine(line_to_plot)

            # if self.arrow:
            #     # Calculate the arrowhead size based on the line width
            #     arrowhead_size = self.stroke * 6.
            #
            #     pen.setWidthF(arrowhead_size)
            #     painter.setPen(pen)
            #
            #     # Calculate the angle of the line
            #     line_angle = math.degrees(math.atan2(line_to_plot.dy(), line_to_plot.dx()))
            #
            #     # Rotate the painter object to match the line orientation
            #     painter.translate(line_to_plot.p2())
            #     painter.rotate(line_angle)
            #     painter.translate(-line_to_plot.p2())
            #
            #     # Extend the line slightly beyond the end point
            #     extended_line = QLineF(line_to_plot.p1(), line_to_plot.p2() + QPointF(arrowhead_size / 2, 0))
            #
            #     # Create a QPainterPath for the arrowhead shape
            #     arrowhead_path = QPainterPath()
            #     arrowhead_path.moveTo(extended_line.p2())
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_size, arrowhead_size / 2))
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_size, -arrowhead_size / 2))
            #     arrowhead_path.closeSubpath()
            #
            #     # Fill the arrowhead shape with the current pen
            #     painter.fillPath(arrowhead_path, pen.brush())


            # if self.arrow:
            #     # Calculate the arrowhead size based on the line width
            #     arrowhead_height = self.stroke * 12
            #     arrowhead_width = self.stroke * 4
            #
            #     # pen.setWidthF(arrowhead_width)
            #     # painter.setPen(pen)
            #
            #     # Calculate the angle of the line
            #     line_angle = math.degrees(math.atan2(line_to_plot.dy(), line_to_plot.dx()))
            #
            #     # Rotate the painter object to match the line orientation
            #     painter.translate(line_to_plot.p2())
            #     painter.rotate(line_angle)
            #     painter.translate(-line_to_plot.p2())
            #
            #     # Extend the line slightly beyond the end point
            #     extended_line = QLineF(line_to_plot.p1(), line_to_plot.p2() + QPointF(arrowhead_width, 0))
            #
            #     # Create a QPainterPath for the arrowhead shape
            #     arrowhead_path = QPainterPath()
            #     arrowhead_path.moveTo(extended_line.p2())
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_height, arrowhead_width))
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_height, -arrowhead_width))
            #     arrowhead_path.closeSubpath()
            #
            #     # Fill the arrowhead shape with the current pen
            #     painter.fillPath(arrowhead_path, pen.brush())
            #
            #     # If arrow_at_both_ends is True, draw a second arrow at the start of the line
            #     # if self.arrow_at_both_ends:
            #     if True:
            #         arrowhead_path = QPainterPath()
            #         arrowhead_base = extended_line.p2() - QPointF(extended_line.length() + arrowhead_width, 0 )
            #         arrowhead_path.moveTo(arrowhead_base)
            #         arrowhead_path.lineTo(arrowhead_base + QPointF(arrowhead_height, arrowhead_width))
            #         arrowhead_path.lineTo(arrowhead_base + QPointF(arrowhead_height, -arrowhead_width))
            #         arrowhead_path.closeSubpath()
            #
            #         # Fill the second arrowhead shape with the current pen
            #         painter.fillPath(arrowhead_path, pen.brush())

            # if self.arrow:
            #     # Calculate the arrowhead size based on the line width
            #     arrowhead_height = self.stroke * 12
            #     arrowhead_width = self.stroke * 4
            #
            #     # Calculate the angle of the line
            #     line_angle = math.degrees(math.atan2(line_to_plot.dy(), line_to_plot.dx()))
            #
            #     # Save the current state of the painter
            #     painter.save()
            #
            #     # Rotate the painter object to match the line orientation for the end arrowhead
            #     painter.translate(line_to_plot.p2())
            #     painter.rotate(line_angle)
            #     painter.translate(-line_to_plot.p2())
            #
            #     # Extend the line slightly beyond the end point
            #     extended_line = QLineF(line_to_plot.p1(), line_to_plot.p2() + QPointF(arrowhead_width, 0))
            #
            #     # Create a QPainterPath for the arrowhead shape
            #     arrowhead_path = QPainterPath()
            #     arrowhead_path.moveTo(extended_line.p2())
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_height, arrowhead_width))
            #     arrowhead_path.lineTo(extended_line.p2() - QPointF(arrowhead_height, -arrowhead_width))
            #     arrowhead_path.closeSubpath()
            #
            #     # Fill the arrowhead shape with the current pen
            #     painter.fillPath(arrowhead_path, pen.brush())
            #
            #     # If arrow_at_both_ends is True, draw a second arrow at the start of the line
            #     if True:
            #         # Restore the painter to its original state
            #         painter.restore()
            #
            #         # Save the current state of the painter
            #         painter.save()
            #
            #         # Rotate the painter object to match the line orientation for the start arrowhead
            #         painter.translate(line_to_plot.p1())
            #         painter.rotate(line_angle + 180)
            #         painter.translate(-line_to_plot.p1())
            #
            #         # Extend the line slightly beyond the start point
            #         extended_line_start = QLineF(line_to_plot.p1() - QPointF(arrowhead_width, 0), line_to_plot.p1())
            #
            #         # Create a QPainterPath for the second arrowhead shape
            #         arrowhead_path = QPainterPath()
            #         arrowhead_path.moveTo(extended_line_start.p1())
            #         arrowhead_path.lineTo(extended_line_start.p1() + QPointF(arrowhead_height, arrowhead_width))
            #         arrowhead_path.lineTo(extended_line_start.p1() + QPointF(arrowhead_height, -arrowhead_width))
            #         arrowhead_path.closeSubpath()
            #
            #         # Fill the second arrowhead shape with the current pen
            #         painter.fillPath(arrowhead_path, pen.brush())
            #
            #         # Restore the painter to its original state
            #         painter.restore()

            if self.arrow:
                # Head size is in drawing units (constant on the page, tied to
                # the stroke), but its POINT is the line's end point itself: the
                # head grows backwards from there. (It used to be pushed
                # stroke*width_scaler beyond the end point, so the tip overshot
                # the pointed feature by an amount that, in image pixels, changed
                # with the panel's scale.)
                stroke = self.stroke if self.stroke is not None else 0.65
                head_length = stroke * self.arrowhead_height_scaler
                head_half_width = stroke * self.arrowhead_width_scaler
                shaft = arrow_shaft(line_to_plot.p1(), line_to_plot.p2(), head_length,
                                    True, bool(self.arrow_at_both_ends))
                if shaft is not None:
                    shaft_pen = QPen(pen)
                    shaft_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
                    painter.setPen(shaft_pen)
                    painter.drawLine(shaft)
                    painter.setPen(pen)
                heads = [(line_to_plot.p1(), line_to_plot.p2())]
                if self.arrow_at_both_ends:
                    heads.append((line_to_plot.p2(), line_to_plot.p1()))
                for tail, tip in heads:
                    geom = arrowhead_polygon(tail, tip, head_length, head_half_width)
                    if geom is not None:
                        painter.fillPath(geom[0], pen.brush())



            painter.restore()
    #
    # def fill(self, painter, draw=True):
    #     if draw:
    #         painter.save()
    #     if self.fill_color is None:
    #         return
    #     painter.setBrush(QBrush(QColor(self.fill_color)))
    #     painter.setOpacity(self.opacity)
    #     if draw:
    #         painter.drawLine(self)
    #         painter.restore()
    #
    # def drawAndFill(self, painter):
    #     painter.save()
    #     self.draw(painter, draw=False)
    #     self.fill(painter, draw=False)
    #     painter.drawLine(self)
    #     painter.restore()

    def __get_scaled_line(self, line_to_plot,scale):
        p1 = line_to_plot.p1()
        p2 = line_to_plot.p2()
        line_to_plot.setP1(QPointF(p1.x() * scale, p1.y() * scale))
        line_to_plot.setP2(QPointF(p2.x() * scale, p2.y() * scale))
        return line_to_plot

    def contains(self, *args):
        # x = 0
        # y = 0
        if isinstance(args[0], QPoint) or isinstance(args[0], QPointF):
            x = args[0].x()
            y = args[0].y()
        else:
            x = args[0]
            y = args[1]
        return self.distToSegment(QPointF(x, y), self.p1(), self.p2()) < 10 and self.boundingContains(*args)

    def lineFromPoints(self, x1, y1, x2, y2):
        a = y2 - y1
        b = x1 - x2
        c = a * x1 + b * y1
        return (a, b, c)

    def len(self, v, w):
        return (v.x() - w.x()) ** 2 + (v.y() - w.y()) ** 2

    def distToSegment(self, p, v, w):
        l2 = self.len(v, w)
        if l2 == 0:
            return self.len(p, v)
        t = ((p.x() - v.x()) * (w.x() - v.x()) + (p.y() - v.y()) * (w.y() - v.y())) / l2
        t = max(0, min(1, t))
        return sqrt(self.len(p, QPointF(v.x() + t * (w.x() - v.x()), v.y() + t * (w.y() - v.y()))))

    def boundingContains(self, *args):
        return self.boundingRect().contains(*args)

    # def boundingRect(self, scaled=True):
    #     scale = 1
    #     if not scaled and self.scale is not None:
    #         scale = self.scale
    #     return QRectF(min(self.p1().x(), self.p2().x()) * scale, min(self.p1().y(), self.p2().y()) * scale,
    #                   abs(self.p2().x() - self.p1().x()) * scale, abs(self.p2().y() - self.p1().y()) * scale)
    # TODO handle scale etc
    def boundingRect(self):
        rect = QRectF(min(self.p1().x(), self.p2().x()), min(self.p1().y(), self.p2().y()),
               abs(self.p2().x() - self.p1().x()), abs(self.p2().y() - self.p1().y()))

        try:
            # print('tada')
            if self.theta is not None and self.theta != 0:
                # print('entering')
                center = rect.center()
                # print('entering2')
                t = QTransform().translate(center.x(), center.y()).rotate(self.theta).translate(-center.x(),
                                                                                                -center.y())
               #  print('entering3')
               #  transformed = self.setTransform(t)
               #  print('entering4')
               #  print(transformed)
               #  print(QRectF(min(transformed.p1().x(), transformed.p2().x()), min(transformed.p1().y(), transformed.p2().y()),
               # abs(transformed.p2().x() - transformed.p1().x()), abs(transformed.p2().y() - transformed.p1().y())))
               #  return QRectF(min(transformed.p1().x(), transformed.p2().x()), min(transformed.p1().y(), transformed.p2().y()),
               # abs(transformed.p2().x() - transformed.p1().x()), abs(transformed.p2().y() - transformed.p1().y()))

                # copy.setT
                # print('entering')

                # t = QTransform().translate( center.x(), center.y()).rotate(self.theta).translate(-center.x(), -center.y())
                # # print('entersd')
                transformed = t.map( self)  #// mapRect() returns the bounding rect of the rotated rect

                # print('rotated',rotatedRect )
                # return rotatedRect
                return QRectF(min(transformed.p1().x(), transformed.p2().x()),
                              min(transformed.p1().y(), transformed.p2().y()),
                abs(transformed.p2().x() - transformed.p1().x()), abs(transformed.p2().y() - transformed.p1().y()))
        except Exception:
            pass
        return rect

    def getRect(self, *args, **kwargs):
        return self.boundingRect()

    def width(self, *args, **kwargs):
        return self.boundingRect().width()

    def height(self, *args, **kwargs):
        return self.boundingRect().height()

    def add(self, *args):
        point = args[1]
        self.setP2(point)
        # self.isSet = True

    def set_to_scale(self, factor):
        self.scale = factor

    # def set_to_translation(self, translation):
    #     self.translation = translation

    # I may really use set and getP1 for points because that is what they are made for !!!
    # def get_P1(self):
    def topLeft(self):
        return self.boundingRect().topLeft()

    # faut pas utiliser ça sinon pbs --> car en fait ce que je veux c'est postionned le point et pas le setter

    def setTopLeft(self, *args):
        if args:
            current_pos = self.boundingRect().topLeft()
            if len(args) == 1:
                point=args[0]
                # assume a QpointF
                # super().moveTopLeft(args[0])
                self.translate(point.x() - current_pos.x(), point.y() - current_pos.y())
                # self.translate(point.x(), point.y())
            elif len(args) == 2:
                # super().moveTopLeft(QPointF(args[0], args[1]))
                self.translate(args[0] - current_pos.x(), args[1] - current_pos.y())
                # self.translate(args[0], args[1])
            else:
                logger.error('invalid args for top left')

    def get_centroid(self):
        return self.x1()+self.x2()/2., self.y1()+self.y2()/2.

    # def set_to_center(self, centroid):
    #     cur_centroid = self.get_centroid()
    #     if isinstance(centroid, (tuple, list)):
    #         self.setX(cur_centroid(0)-centroid(0))
    #         self.setY(cur_centroid(1)-centroid(1))
    #     else:
    #         self.setX(cur_centroid(0)-centroid.x())
    #         self.setY(cur_centroid(1)-centroid.y())

    def set_to_center(self, centroid):
        if isinstance(centroid, (tuple, list)):
            self.setX(centroid[0]-self.width()/2.)
            self.setY(centroid[1]-self.height()/2.)
        else:
            self.setX(centroid.x()-self.width()/2.)
            self.setY(centroid.y()-self.height()/2.)


    # def set_P1(self, point):
    # def setTopLeft(self, point):
    #     current_pos = self.boundingRect().topLeft()
    #     self.translate(point.x() - current_pos.x(), point.y() - current_pos.y())
    #     # self.translate(self.translation)
    #     # if not args:
    #     #     logger.error("no coordinate set...")
    #     #     return
    #     # if len(args) == 1:
    #     #     self.setP1(args[0])
    #     # else:
    #     #     self.setP1(QPointF(args[0], args[1]))


    # def set_P2(self,*args):
    #     if not args:
    #         logger.error("no coordinate set...")
    #         return
    #     if len(args) == 1:
    #         self.setP2(args[0])
    #     else:
    #         self.setP2(QPointF(args[0], args[1]))

    def erode(self, nb_erosion=1):
        self.__computeNewMorphology(sizeChange=-nb_erosion)

    def dilate(self, nb_dilation=1):
        self.__computeNewMorphology(sizeChange=nb_dilation)

    def __computeNewMorphology(self, sizeChange=1):
        # grow (or shrink) the line by sizeChange px at each end, around its centre;
        # it never gets shorter than 1 px
        length = self.length()
        if length == 0:
            return
        final_length = max(1., length + 2. * sizeChange)
        factor = final_length / length
        c = (self.p1() + self.p2()) / 2.
        self.setP1(c + (self.p1() - c) * factor)
        self.setP2(c + (self.p2() - c) * factor)

    def __repr__(self):
        class_name = type(self).__name__
        memory_address = hex(id(self))
        if self.arrow:
            class_name='Arrow2D'
        return f"{class_name}-{memory_address}"

    def to_dict(self):
        x1 = self.x1()
        x2 = self.x2()
        y1 = self.y1()
        y2 = self.y2()

        # Create a dictionary representation of the values of the super object
        output_dict = {
            'x1': x1,
            'y1': y1,
            'x2': x2,
            'y2': y2,
        }
        # Update the dictionary with the __dict__ of Rectangle2D
        output_dict.update(self.__dict__)
        return output_dict

if __name__ == '__main__':
    # ça marche --> voici deux examples de shapes
    test = Line2D(0, 0, 100, 100, arrow=True)

    print(test.lineFromPoints(0, 0, 100, 100))
    print(test.contains(0, 0))  # true
    print(test.contains(10, 10))  # true
    print(test.contains(-10, -10))  # false # on line with that equation but outside range
    print(test.contains(0, 18))  # false

    p1 = test.p1()
    print(p1.x(), p1.y())
    p2 = test.p2()
    print(p2.x(), p2.y())
    print(test.arrow)
    print(test.length())  # sqrt 2 --> 141
    # if it's an arrow I can add easily all the stuff I need

    test = Line2D(0, 0, 1, 1)
    p1 = test.p1()
    print(p1.x(), p1.y())
    p2 = test.p2()
    print(p2.x(), p2.y())
    print(test.arrow)
    import math

    print(test.length() == sqrt(2))  # sqrt 2

    test2 = Line2D()
    p1 = test2.p1()
    print(p1.x(), p1.y())
    p2 = test2.p2()
    print(p2.x(), p2.y())
    print(test2.arrow)

    # TODO add preview as an image to gain time --> TODO
