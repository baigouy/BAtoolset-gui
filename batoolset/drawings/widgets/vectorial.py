# TODO -−> add the small displacement filtering there!!! --> jut copy it from the other code -−> should be easy and maybe it would be useful to have a list of shapes so that one can delete them -−> see if I add that as  separate stuff!!!
# I could also save the polygonF maybe


import os
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from batoolset.drawings.shapes.txt2d import TAText2D
from batoolset.pyqts.tools import getCtrlModifier
from qtpy import QtCore
from batoolset.drawings.shapes.polygon2d import Polygon2D
from batoolset.drawings.shapes.line2d import Line2D
from batoolset.drawings.shapes.rect2d import Rect2D
from batoolset.drawings.shapes.square2d import Square2D
from batoolset.drawings.shapes.ellipse2d import Ellipse2D
from batoolset.drawings.shapes.circle2d import Circle2D
from batoolset.drawings.shapes.freehand2d import Freehand2D
from batoolset.drawings.shapes.point2d import Point2D
from batoolset.drawings.shapes.polyline2d import PolyLine2D
from batoolset.drawings.shapes.image2d import Image2D
from qtpy.QtCore import QPointF, QRectF
from batoolset.tools.logger import TA_logger # logging
logger = TA_logger()

class VectorialDrawPane:

    def __init__(self, active=False, demo=False, scale=1.0, drawing_mode=False, extra_size_for_sel=0, filter_out_unwanted_shapes_based_on_distance=True):
        self.shapes = []
        self.currently_drawn_shape = None
        self.shape_to_draw = None
        self.selected_shape = []
        self.active = active
        self.scale = scale
        self.drawing_mode = drawing_mode
        self.extra_size_for_sel = extra_size_for_sel # can be used to add an extra size around very small shapes --> TODO
        self.filter_out_unwanted_shapes_based_on_distance = filter_out_unwanted_shapes_based_on_distance  # if set to True the tool will attempt to filter accidental drawings by the user (based on distance between draw points)
        if demo:
            self.shapes.append(Polygon2D(0, 0, 10, 0, 10, 20, 0, 20, 0, 0, color=0x00FF00))
            self.shapes.append(
                Polygon2D(100, 100, 110, 100, 110, 120, 10, 120, 100, 100, color=0x0000FF, fill_color=0x00FFFF,
                          stroke=2))
            self.shapes.append(Line2D(0, 0, 110, 100, color=0xFF0000, stroke=3))
            self.shapes.append(Rect2D(200, 150, 250, 100, stroke=10))
            self.shapes.append(Square2D(300, 260, 250, stroke=3))
            self.shapes.append(Ellipse2D(0, 50, 600, 200, stroke=3))
            self.shapes.append(Circle2D(150, 300, 30, color=0xFF0000))
            self.shapes.append(PolyLine2D(10, 10, 20, 10, 20, 30, 40, 30, color=0xFF0000, stroke=2))
            self.shapes.append(PolyLine2D(10, 10, 20, 10, 20, 30, 40, 30, color=0xFF0000, stroke=2))
            self.shapes.append(Point2D(128, 128, color=0xFF0000, stroke=6))
            self.shapes.append(Point2D(128, 128, color=0x00FF00, stroke=1))
            self.shapes.append(Point2D(10, 10, color=0x000000, stroke=6))
            img0 = Image2D('/E/Sample_images/counter/00.png')
            img1 = Image2D('/E/Sample_images/counter/01.png')
            img2 = Image2D('/E/Sample_images/counter/02.png')
            img3 = Image2D('/E/Sample_images/counter/03.png')
            img4 = Image2D('/E/Sample_images/counter/04.png')
            img5 = Image2D('/E/Sample_images/counter/05.png')
            img6 = Image2D('/E/Sample_images/counter/06.png')
            img7 = Image2D('/E/Sample_images/counter/07.png')
            img8 = Image2D('/E/Sample_images/counter/08.png')
            img9 = Image2D('/E/Sample_images/counter/09.png')
            img10 = Image2D('/E/Sample_images/counter/10.png')

            row = img1 + img2 + img10

            self.shapes.append(row)

            row2 = img4 + img5
            fig = row / row2
            # fig = Column(row, row2)
            #self.shapes.append(fig)
            self.drawing_mode = True
            # self.shape_to_draw = Line2D
            # self.shape_to_draw = Rect2D
            # self.shape_to_draw = Square2D
            # self.shape_to_draw = Ellipse2D
            # self.shape_to_draw = Circle2D
            # self.shape_to_draw = Point2D  # ok maybe small centering issue
            # self.shape_to_draw = Freehand2D
            # self.shape_to_draw = PolyLine2D
            # self.shape_to_draw = Polygon2D
            import random
            drawing_methods = [Line2D, Rect2D, Square2D, Ellipse2D, Circle2D, Point2D, Freehand2D, PolyLine2D, Polygon2D]
            self.shape_to_draw = random.choice(drawing_methods)

            # TODO freehand drawing
            # TODO broken line --> need double click for end

    def paintEvent(self, *args):
        painter = args[0]
        visibleRect = None
        if len(args) >= 2:
              visibleRect = args[1]

        painter.save()
        if self.scale != 1.0:
            painter.scale(self.scale, self.scale)

        for shape in self.shapes:
            # only draw shapes if they are visible --> requires a visiblerect to be passed
            if visibleRect is not None:
                # only draws if in visible rect
                if shape.boundingRect().intersects(QRectF(visibleRect)):
                    shape.draw(painter)
            else:
                shape.draw(painter)

        if self.currently_drawn_shape is not None:
            if self.currently_drawn_shape.isSet:
                self.currently_drawn_shape.draw(painter)

        sel = self.create_master_rect()
        if sel is not None:
            painter.drawRect(sel)
        painter.restore()
        # painter.end() # probably a good idea ????

    def group_contains(self, x, y):
        # checks if master rect for group contains click
        # get bounds and create union and compare
        master_rect = self.create_master_rect()
        if master_rect is None:
            return False
        return master_rect.contains(QPointF(x, y))

    def create_master_rect(self):
        master_rect = None
        if self.selected_shape:
            for shape in self.selected_shape:
                if master_rect is None:
                    master_rect = shape.boundingRect()
                else:
                    master_rect = master_rect.united(shape.boundingRect())
        return master_rect

    def removeCurShape(self):
        if self.selected_shape:
            self.shapes = [e for e in self.shapes if e not in self.selected_shape]
            self.selected_shape = []

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.drawing = True
            self.lastPoint = event.position() / self.scale
            self.firstPoint = event.position() / self.scale

            shapeFound = False
            if self.currently_drawn_shape is None:
                for shape in reversed(self.shapes):
                    if shape.contains(self.lastPoint, extra=self.extra_size_for_sel) and not shape in self.selected_shape:
                        logger.debug('you clicked shape:' + str(shape))
                        if event.modifiers() == getCtrlModifier():
                            if shape not in self.selected_shape:  # avoid doublons
                                self.selected_shape.append(shape)  # add shape to group
                                logger.debug('adding shape to group')
                                # shapeFound = True
                        else:
                            if not self.group_contains(self.lastPoint.x(), self.lastPoint.y()):
                                self.selected_shape = [shape]
                                logger.debug('only one element is selected')
                                # shapeFound = True
                        return

                if not shapeFound and event.modifiers() == getCtrlModifier():
                    for shape in reversed(self.shapes):
                        if shape.contains(self.lastPoint, extra=self.extra_size_for_sel):
                            if shape in self.selected_shape:  # avoid doublons
                                logger.debug('you clicked again shape:' + str(shape))
                                self.selected_shape.remove(shape)  # add shape to group
                                logger.debug('removing a shape from group')
                                shapeFound = True
                # no shape found --> reset sel
                if not shapeFound and not self.group_contains(self.lastPoint.x(), self.lastPoint.y()):
                    logger.debug('resetting sel')
                    self.selected_shape = []

            # check if a shape is selected and only move that
            if self.drawing_mode and not self.selected_shape and self.currently_drawn_shape is None:
                # do not reset shape if not done drawing...
                if self.shape_to_draw is not None:
                    self.currently_drawn_shape = self.shape_to_draw()
                else:
                    self.currently_drawn_shape = None
            if self.drawing_mode and not self.selected_shape:
                if self.currently_drawn_shape is not None:
                    self.currently_drawn_shape.setTopLeft(QPointF(self.lastPoint.x(), self.lastPoint.y()))

    def mouseMoveEvent(self, event):
        if event.buttons() and QtCore.Qt.LeftButton:
            if self.selected_shape and self.currently_drawn_shape is None:
                logger.debug('moving' + str(self.selected_shape))
                for shape in self.selected_shape:
                    shape.translate(event.position() / self.scale - self.lastPoint)

        if self.currently_drawn_shape is not None:
            self.currently_drawn_shape.add(self.firstPoint, self.lastPoint)

        self.lastPoint = event.position() / self.scale

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.position() / self.scale
            self.drawing = False
            if self.drawing_mode and self.currently_drawn_shape is not None:
                self.currently_drawn_shape.add(self.firstPoint, self.lastPoint)
                if isinstance(self.currently_drawn_shape, Freehand2D):
                    # this closes the freehand shape
                    self.currently_drawn_shape.add(self.lastPoint, self.firstPoint)
                # should not erase the shape if it's a polyline or a polygon by the way
                if isinstance(self.currently_drawn_shape, Freehand2D) or (not isinstance(self.currently_drawn_shape, PolyLine2D) and not isinstance(self.currently_drawn_shape, Polygon2D)):
                    if self.check_shape_size_before_adding_it():
                        self.shapes.append(self.currently_drawn_shape)
                        self.selected_shape = [self.currently_drawn_shape]
                        self.currently_drawn_shape = None
                    else:
                        self.currently_drawn_shape = None
                        self.selected_shape = []

        else:
            self.currently_drawn_shape=None
            self.selected_shape = []

    def mouseDoubleClickEvent(self, event):
        if isinstance(self.currently_drawn_shape, PolyLine2D) or isinstance(self.currently_drawn_shape, Polygon2D):
            self.shapes.append(self.currently_drawn_shape)
            self.currently_drawn_shape = None

    def check_shape_size_before_adding_it(self):
        if self.filter_out_unwanted_shapes_based_on_distance:  # TODO maybe allow arrowheads to be drawn and stay small, allow lines only if they are in arrwohed only mode (if so do not allow the body of the li,ne to be drawn)
            # if the movement is too small and the object is not a point then the shape drawing is probably undesised!!!
            # print(self.firstPoint , self.lastPoint)
            # print('distance', self.distance(self.firstPoint, self.lastPoint))
            # print('scaled distance', self.distance(self.firstPoint, self.lastPoint)*self.scale)
            # if self.distance(self.firstPoint, self.lastPoint) < 20:
            # best is to look
            # print(self.currently_drawn_shape.getRect())
            rect = self.currently_drawn_shape.getRect()

            print(rect, self.scale)


            print('area to check',rect.width()* rect.height()*self.scale)
            if not isinstance(self.currently_drawn_shape,(Point2D, TAText2D, Line2D)) and rect.width()* rect.height()*self.scale<200:


            # if not isinstance(self.currently_drawn_shape,(Point2D)) and self.distance(self.firstPoint,self.lastPoint) * self.scale < 40: # , Polygon2D, PolyLine2D, Freehand2D)
                logger.warning(str(self.currently_drawn_shape) + '-->' +
                               'area of object is too small, drawing is ignored, the software assumes unintended drawing, zoom more (Ctrl/Cmd +) and redraw the shape if wanted')
                self.currently_drawn_shape = None
                # self.update()
                # print(distance )
                return False
            return True

if __name__ == '__main__':
    VectorialDrawPane()
