import os
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from math import sqrt

from qtpy.QtCore import QRectF

from batoolset.drawings.shapes.circle2d import *
from batoolset.tools.logger import TA_logger
logger = TA_logger()

class Point2D(QPointF):

    def __init__(self, *args, x=0,y=0, color=0xFFFFFF, fill_color=None, opacity=1., stroke=0.65, line_style=None,__version__=1.0, **kwargs):
        # self.isSet = True
        self.size = 5
        if len(args)==2:
            #TODO need fix size
            super(Point2D, self).__init__(*args)
        else:
            # self.size = 5
            if args:
                super(Point2D, self).__init__(*args) # create an empty point for drawing
            else:
                super(Point2D, self).__init__(x,y)

        if stroke is not None and stroke > 2:
            self.size = stroke
        self.color = color
        self.fill_color = fill_color
        self.stroke = stroke
        self.opacity = opacity
        self.theta = 0 # useless for a point but useful for compat
        self.scale = 1
        self.translation = QPointF()
        self.line_style = line_style
        self.__version__ = __version__

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

    def contains(self, *args):
      x=0
      y=0
      if isinstance(args[0], QPoint) or isinstance(args[0], QPointF):
          x = args[0].x()
          y = args[0].y()
      if sqrt((x-self.x())**2+(y-self.y())**2)<10:
          return True
      return False

    def translate(self, *translation):
        # if isinstance(translation, (QPoint, QPointF)):
        if isinstance(translation[0], (int, float)):
            translation = QPointF(translation[0], translation[1])

        if isinstance(translation, tuple):
            # not sure this is normal that I have to do that but if I don't do it dragging the ellipse in the demo image crashes the soft
            translation = QPointF(translation[0])

        self.setX(self.x() + translation.x())
        self.setY(self.y() + translation.y())

    def draw(self, painter, draw=True, parent=None):
        if self.color is None and self.fill_color is None:
            return

        if draw:
            painter.save()
            painter.setOpacity(self.opacity)
            if self.color is not None:
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
            else:
                painter.setPen(Qt.NoPen)  # required to draw something filled without a border
            if self.fill_color is not None:
                painter.setBrush(QBrush(QColor(self.fill_color)))
            point_to_draw = QPointF(self.x(), self.y())

            # print('point_to_draw', point_to_draw)

            if parent is not None and parent.scale is not None and parent.scale != 1:
                point_to_draw = QPointF(point_to_draw.x()/parent.scale, self.y()/parent.scale)

            if parent is not None:
                point_to_draw = QPointF(point_to_draw.x()+parent.x(), point_to_draw.y()+parent.y())

            # print('point_to_draw2', point_to_draw)

            # if self.scale is not None and self.scale != 1:
            #     point_to_draw.setX(point_to_draw.x()*self.scale)
            #     point_to_draw.setY(point_to_draw.y()*self.scale)
            # if self.translation is not None:
            #     point_to_draw.setX(point_to_draw.x()+self.translation.x())
            #     point_to_draw.setY(point_to_draw.y()+self.translation.y())

            # painter.drawEllipse(point_to_draw.x()-self.stroke/2., point_to_draw.y()-self.stroke/2, self.stroke, self.stroke)
            painter.drawEllipse(int(point_to_draw.x()-self.stroke/2.), int(point_to_draw.y()-self.stroke/2), int(self.stroke), int(self.stroke)) # why tale int here --> draw in float precision --> because there is no simple ellipse object in pyqt -−> see my ellipse implementation --> and fix that some day!!
            # painter.drawEllipse(point_to_draw.x()-self.stroke/2., point_to_draw.y()-self.stroke/2, self.stroke, self.stroke) # why tale int here --> draw in float precision
            painter.restore()

    # def fill(self, painter, draw=True):
    #     if self.fill_color is None:
    #         return
    #     if draw:
    #         painter.save()
    #     painter.setBrush(QBrush(QColor(self.fill_color)))
    #     painter.setOpacity(self.opacity)
    #     if draw:
    #         painter.drawEllipse(self.x()-self.stroke/2., self.y()-self.stroke/2, self.stroke, self.stroke)
    #         painter.restore()
    #
    # def drawAndFill(self, painter):
    #     painter.save()
    #     self.draw(painter, draw=False)
    #     self.fill(painter, draw=False)
    #     size = max(self.size, self.stroke)
    #     painter.drawEllipse(self.x()-size/2., self.y()-size/2, size, size) # drawEllipse (x, y, w, h)
    #     painter.restore()

    def boundingRect(self):
        return QRectF(self.x()-self.stroke/2., self.y()-self.stroke/2, self.stroke, self.stroke)

    def add(self, *args):
        point = args[1]
        self.setX(point.x())
        self.setY(point.y())

    # def set_P1(self, *args):
    #     if not args:
    #         logger.error("no coordinate set...")
    #         return
    #     if len(args) == 1:
    #         # self.moveTo(args[0].x(), args[0].y())
    #         self.setX(args[0].x())
    #         self.setY(args[0].y())
    #     else:
    #         # self.moveTo(QPointF(args[0], args[1]))
    #         self.setX(args[0])
    #         self.setY(args[1])
    #     # self.setX(point.x())
    #     # self.setY(point.y())

    # def get_P1(self):
    #     return self
    def setTopLeft(self, *args):
        if args:
            if len(args)==1:
                # assume a QpointF
                super().setP1(args[0])
            elif len(args)==2:
                super().setP1(QPointF(args[0], args[1]))
            else:
                logger.error('invalid args for top left')


    def topLeft(self):
        return self

    def getRect(self, *args, **kwargs):
        return self.boundingRect()

    def width(self):
        return 0

    def height(self):
        return 0

    def set_to_scale(self, factor):
        self.scale = factor

    def set_to_translation(self, translation):
        self.translation = translation

    def set_to_center(self, centroid):
        if isinstance(centroid, (tuple, list)):
            self.setX(centroid[0])
            self.setY(centroid[1])
        else:
            self.setX(centroid.x())
            self.setY(centroid.y())

    def __repr__(self):
        class_name = type(self).__name__
        memory_address = hex(id(self))
        return f"{class_name}-{memory_address}"

    def to_dict(self):
        x = self.x()
        y = self.y()

        # Create a dictionary representation of the values of the super object
        output_dict = {
            'x': x,
            'y': y,
        }
        # Update the dictionary with the __dict__ of Rectangle2D
        output_dict.update(self.__dict__)
        return output_dict

if __name__ == '__main__':
    # ça marche --> voici deux examples de shapes
    test = Point2D(128, 128)
    # print(test.x(), test.y(), test.width(), test.height())
    print(test.contains(QPointF(128, 128)))
    print(test.contains(QPointF(129, 129))) # why True ??? --> maybe ok but think
    print(test.contains(QPointF(-1, -1)))
    print(test.contains(QPointF(0, 0)))
    print(test.contains(QPointF(100, 100)))
    print(test.contains(QPointF(100, 100.1)))
    print(test.x())
    print(test.y())
    print(test.translate(QPoint(10, 10)))
    print(test.x())
    print(test.y())

    # p1 = test.p1()
    # print(p1.x(), p1.y())
    # p2 = test.p2()
    # print(p2.x(), p2.y())
    # print(test.arrow)
    # print(test.length()) # sqrt 2 --> 141
    # # if it's an arrow I can add easily all the stuff I need
    #
    # test = Rect2D(0, 0, 1, 1)
    # p1 = test.p1()
    # print(p1.x(), p1.y())
    # p2 = test.p2()
    # print(p2.x(), p2.y())
    # print(test.arrow)
    # import math
    # print(test.length() == math.sqrt(2))  # sqrt 2
    #
    # test2 = Rect2D()
    # p1 = test2.p1()
    # print(p1.x(), p1.y())
    # p2 = test2.p2()
    # print(p2.x(), p2.y())
    # print(test2.arrow)
