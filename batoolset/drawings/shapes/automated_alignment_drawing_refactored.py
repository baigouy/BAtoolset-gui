from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
import random
import sys
from qtpy.QtGui import QTransform,QPolygon
from qtpy.QtWidgets import QApplication, QWidget
from qtpy.QtGui import QPainter, QPen, QBrush, QColor
from qtpy.QtCore import Qt, QPointF, QRectF,QPoint
from batoolset.drawings.shapes.polyline2d import PolyLine2D
from batoolset.drawings.shapes.transform2D import get_centroid, get_points, Transform2D

def compute_translation_corrections(img1, minimal_return=True):
    old_scale = img1.scale
    img1.set_to_scale(1.)

    parent_rect = QRectF(img1.getRect(raw=True))
    parent_rect = QRectF(0, 0, parent_rect.width(), parent_rect.height())

    theta = img1.theta
    if not theta:
        theta=0
    crop_left = img1.crop_left
    crop_right = img1.crop_right
    crop_top = img1.crop_top
    crop_bottom = img1.crop_bottom
    if not crop_left:
        crop_left=0
    if not crop_right:
        crop_right=0
    if not crop_top:
        crop_top=0
    if not crop_bottom:
        crop_bottom=0

    center_parent = parent_rect.center()
    transform = QTransform()
    transform.translate(-center_parent.x(), -center_parent.y())
    transform.rotate(theta)
    transform.translate(center_parent.x(), center_parent.y())
    rotated_rect = transform.mapToPolygon(parent_rect.toRect())  # this is the center versio n
    rotated_rect_bounds = transform.mapRect(parent_rect)
    trans = parent_rect.center() - rotated_rect_bounds.center()  # this is the center version
    rotated_rect_bounds.translate(trans)
    rotated_rect_before_trans = QPolygon(rotated_rect)
    rotated_rect.translate(int(trans.x()), int(trans.y()))  # --> error --> this stuff is not at the right place
    crop_rect = QRectF(rotated_rect_bounds.x() + crop_left, rotated_rect_bounds.y() + crop_top,
                            rotated_rect_bounds.width() - crop_right - crop_left,
                            rotated_rect_bounds.height() - crop_top - crop_bottom)
    rect = crop_rect
    centroid_of_crop = get_centroid(get_points(rect))

    center_before_reg = get_centroid(get_points(rotated_rect_before_trans))
    rotated_rect_before_trans.translate(-int(center_before_reg[0] - centroid_of_crop[0]),
                                             -int(center_before_reg[1] - centroid_of_crop[1]))

    fixing_error_trans = img1.getRect(all=True).center() - crop_rect.center()
    extra_fix = QPointF(
        rotated_rect_before_trans.boundingRect().center() - rotated_rect.boundingRect().center())  # now it is perfectly aligned to the light cyan rect -−> how cna I realign it now to the cyan rect
    fixing_error_trans += extra_fix
    extra_user_translation = (fixing_error_trans.x(), fixing_error_trans.y())

    img1.set_to_scale(old_scale)

    # bug fix if image is not at 0,0, remove extra useless translation
    extra_user_translation = (extra_user_translation[0]-img1.x(), extra_user_translation[1]-img1.y())

    if minimal_return:
        return extra_user_translation,rotated_rect.boundingRect().center() - rotated_rect_before_trans.boundingRect().center()
    else:
        return centroid_of_crop,center_parent, rotated_rect_before_trans, crop_rect, parent_rect, rotated_rect_bounds, rotated_rect, extra_user_translation,rotated_rect.boundingRect().center()-rotated_rect_before_trans.boundingRect().center()
#
# class AutomaticDrawingOfRegistrationRect(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         self.MODE_CHECK = True # I fTrue uses the default mode
#
#         self.theta = random.randint(-359, 359)
#         self.theta = 42
#         self.theta = 0
#
#         lines = [
#             (0, 0, 0, 0),
#             (30, 40, 60, 80),
#             (90, 10, 33, 16),
#             (60, 30, 0, 0), # this one seems buggy
#             (60, 0, 0, 0),
#             (90, 0, 0, 0),
#             (0, 60, 0, 0),
#             (0, 90, 0, 0),
#             (60, 60, 0, 0),
#             (60, 60, 40, 40),
#             (0, 0, 40, 40),
#             (0, 0, 0, 40),
#             (0, 0, 0, 90),
#             (0, 0, 40, 0),
#             (0, 0, 90, 0),
#             (60, 0, 40, 0),
#             (60, 0, 0, 40),
#             (0, 60, 0, 40),
#             (0, 60, 40, 0),
#             (0, 60, 40, 30),
#             (60, 0, 40, 30),
#             (60, 40, 0, 30),
#             (60, 40, 50, 0),
#             (30, 70, 10, 0)
#         ]
#
#         # Randomly select a line and execute it
#         self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = random.choice(lines)
#
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 0, 0
#         self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 30, 40, 60, 80
#         self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 30, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 90, 10, 33, 16
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 0, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 90, 0, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 60, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 90, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 60, 0, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 60, 40, 40
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 40, 40
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 0, 40
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 0, 90
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 40, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 0, 90, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 0, 40, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 0, 0, 40
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 60, 0, 40
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 60, 40, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 0, 60, 40, 30
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 0, 40, 30
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 40, 0, 30
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 60, 40, 50, 0
#         # self.crop_left, self.crop_right, self.crop_top, self.crop_bottom = 30, 70, 10, 0
#
#         from pyfigures.gui.keep_tst_images_for_pzf import get_complex_tst_image
#         img1 = get_complex_tst_image()
#         img1.set_rotation(self.theta)
#         img1.crop(self.crop_left, self.crop_right, self.crop_top, self.crop_bottom)
#         # img1.set_to_scale(1) # make sure it is full size
#         self.img = img1
#
#         # if there is scaling --> there is an error --> try to see why that is
#         # self.img.set_to_scale(1./0.3)
#
#         print(self.img.scale)
#         self.img.scale=1 # apparently the bug is there
#         # self.img.scale=1/0.3 # apparently the bug is there # ok --> now scale is finally supported --> very good
#         # self.img.scale=2
#
#         # test of all
#
#         self.centroid_of_crop, self.center_parent, self.rotated_rect_before_trans, self.crop_rect, self.parent_rect, self.rotated_rect_bounds, self.rotated_rect, extra_user_translation, self.extra_translation_at_painter = compute_translation_corrections(img1, minimal_return=False)
#
#         if not self.MODE_CHECK:
#             self.img.extra_user_translation = extra_user_translation
#         else:
#             self.img.extra_user_translation = (0,0)
#
#         self.rect = self.crop_rect
#
#         print('extra_user_translation', extra_user_translation)
#         print('extra_translation_at_painter', self.extra_translation_at_painter)
#         # print('fixing_error_trans', self.fixing_error_trans)
#
#         self.line_length = 10  # pixels
#         self.colors = [QColor(Qt.red), QColor(Qt.green), QColor(Qt.blue), QColor(Qt.yellow)]
#
#         self.center_after_reg = get_centroid(get_points(self.rotated_rect_before_trans))
#
#         points_of_unrotated_rect = get_points(self.rect)
#         trafo2D = Transform2D()
#         trafo2D.translate(self.center_parent.x(), self.center_parent.y())
#         trafo2D.rotate(-self.theta)
#         trafo2D.translate(-self.center_parent.x(), -self.center_parent.y())
#
#         # this will give me the rect to plot on the parent -−> quite easy
#         rotated_back_points = trafo2D.apply(points_of_unrotated_rect)
#         self.fixed_center = get_centroid(rotated_back_points)
#
#         self.setMinimumSize(800,600)
#         self.update()
#
#
#     def draw_alignment_rect(self, painter):
#         painter.setPen(QColor(0, 0, 0))
#
#         # Draw the crop values as text
#         painter.drawText(10, 20, f"Crop Left: {self.crop_left}")
#         painter.drawText(10, 40, f"Crop Right: {self.crop_right}")
#         painter.drawText(10, 60, f"Crop Top: {self.crop_top}")
#         painter.drawText(10, 80, f"Crop Bottom: {self.crop_bottom}")
#         painter.drawText(10, 100, f"Angle: {self.theta }")
#
#         painter.translate(256, 256) # just to better visualize and understand all !! -> TODO
#
#         if True:
#             random_number = random.uniform(0.1, 3.0)
#             painter.scale(random_number,random_number) # ça marche et c'est scale insensitive --> TODO à fixer
#
#
#
#         if True:
#             painter.save()
#             # if not (self.crop_left and self.crop_right and self.crop_top and self.crop_bottom):
#             # if False:
#             if True:
#                 painter.translate((self.crop_rect.center() - self.img.getRect(all=True).center())/self.img.scale) # very good -> this is sufficient to align the center to that
#                 # this is just to center the image this stuff is in fact largely usless!!!
#
#                 # pass
#             # painter.translate(self.center_after_reg[0]- self.img.getRect(all=True).center().x(),self.center_after_reg[1]- self.img.getRect(all=True).center().y()) # very good -> this is sufficient to align the center to that
#             # painter.translate(self.center_after_reg[0]- self.img.getRect(all=True).center().x(),self.center_after_reg[1]- self.img.getRect(all=True).center().y()) # very good -> this is sufficient to align the center to that
#             # painter.translate(self.rotated_rect.boundingRect().center().x()-self.img.getRect(all=True).center().x(),self.rotated_rect.boundingRect().center().y()-self.img.getRect(all=True).center().y()) # very good -> this is sufficient to align the center to that
#             # rotated center centered on that
#             self.img.draw_bg(painter, restore_painter_in_the_end=True)
#
#             # this is the really important stuff and again it should be scaled
#             # painter.translate(self.rotated_rect.boundingRect().center()-self.rotated_rect_before_trans.boundingRect().center()) # ça marche is je met le truc ici --> par contre est ce que je controle la position ???
#             if not self.MODE_CHECK:
#             # if True:
#                 painter.translate(self.extra_translation_at_painter/self.img.scale)  # ça marche is je met le truc ici --> par contre est ce que je controle la position ???
#
#             self.img.draw_annotations(painter, restore_painter_in_the_end=False)
#             painter.restore()
#
#         # Reset the clipping region
#         # painter.setClipping(False)
#
#         shapes_drawn = []
#
#         pen = QPen(Qt.lightGray, 6)
#         painter.setPen(pen)
#         # Draw the rectangle
#         painter.drawRect(self.parent_rect)
#         pen.setWidthF(24)
#         painter.setPen(pen)
#         painter.drawPoint(self.parent_rect.center())  # ok
#
#         pen = QPen(Qt.yellow, 6)
#         painter.setPen(pen)
#         # Draw the rectangle
#         painter.drawRect(self.rotated_rect_bounds)
#         pen.setWidthF(12)
#         painter.setPen(pen)
#         painter.drawPoint(self.rotated_rect_bounds.center())  # ok
#
#         pen = QPen(Qt.cyan,6)
#         painter.setPen(pen)
#         painter.drawPolygon(self.rotated_rect)
#         painter.drawPoint(self.rotated_rect.boundingRect().center())
#
#         # pen = QPen(QColor(224, 128, 255), 6)  # lighcyan
#         pen = QPen(QColor(255, 0, 0), 1)  # lighcyan
#         painter.setPen(pen)
#         painter.drawPolygon(self.rotated_rect_before_trans)
#         pen.setWidthF(12)
#         painter.setPen(pen)
#         painter.drawPoint(
#             self.rotated_rect_before_trans.boundingRect().center())  # this is aligned with the the centroid of crop probably by construction
#
#         # painter.save()
#         # painter.translate(-center_parent.x(), -center_parent.y())
#         # painter.rotate(self.theta)
#         # painter.translate(center_parent.x(), center_parent.y())
#
#         pen = QPen(Qt.darkGray, 6)
#         painter.setPen(pen)
#         # Draw the rectangle
#         painter.drawRect(self.rect)
#         painter.drawPoint(int(self.centroid_of_crop[0]), int(self.centroid_of_crop[1]))  # ok
#
#         # maybe get the center of the rotated back shit
#
#         if True:
#             # this belongs to the unrotated rect that I never plotted
#             pen = QPen(Qt.red, 3)
#             painter.setPen(pen)
#             painter.drawPoint(int(self.fixed_center[0]),int(self.fixed_center[1]))  # ok
#
#         # now put the extra correction
#         # maybe it is one of these centroids that I should use
#
#         # painter.restore()
#
#         # Draw two orthogonal lines at each corner with unique colors
#         corners = [self.rect.topLeft(), self.rect.topRight(), self.rect.bottomLeft(), self.rect.bottomRight()]
#         for i, point in enumerate(corners):
#             x, y = point.x(), point.y()
#             sign_x, sign_y = 1, 1
#             if i in [1, 3]:
#                 sign_x = -1
#             if i in [2, 3]:
#                 sign_y = -1
#             painter.setPen(QPen(self.colors[i], 2))
#             painter.drawLine(point, QPointF(x + self.line_length * sign_x, y))
#             painter.drawLine(point, QPointF(x, y + self.line_length * sign_y))
#             # test = PolyLine2D(*[x + self.line_length * sign_x, x,y, x,y,  x , y + self.line_length * sign_y])
#             corner = PolyLine2D(x + self.line_length * sign_x, y, x, y, x, y, x, y + self.line_length * sign_y, stroke=1,
#                               color=self.colors[i].toRgb())
#             # corner.draw(painter)
#             shapes_drawn.append(corner)
#
#             # print(test.count())
#
#         # Draw a cross at the center
#         center = self.rect.center()
#         pen = QPen(QColor(Qt.magenta), 2)
#         painter.setPen(pen)
#         painter.drawLine(QPointF(center.x() - self.line_length, center.y()),
#                          QPointF(center.x() + self.line_length, center.y()))
#         painter.drawLine(QPointF(center.x(), center.y() - self.line_length),
#                          QPointF(center.x(), center.y() + self.line_length))
#         horiz = PolyLine2D(center.x() - self.line_length, center.y(), center.x() + self.line_length, center.y(),
#                            stroke=1,
#                            color=QColor(Qt.magenta).toRgb())
#         vert = PolyLine2D(center.x(), center.y() - self.line_length, center.x(), center.y() + self.line_length,
#                           stroke=1,
#                           color=QColor(Qt.magenta).toRgb())
#         # horiz.draw(painter)
#         # vert.draw(painter)
#         shapes_drawn.append(horiz)
#         shapes_drawn.append(vert)
#         return shapes_drawn
#
#     def paintEvent(self, event):
#         painter = QPainter(self)
#
#         shapes_drawn = self.draw_alignment_rect(painter)
#
#         # Now I could try to really map these shapes on the real image!!!
#
#         # print(shapes_drawn)
#         painter.end()
#         # the shapes and te lines are now ok --> I can then use them to register the fake image and compute the messed up translation --> TODO
#
#         # convert this also to a polyline line object so that I can draw it!!!
#         # see how I can do that
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     widget = AutomaticDrawingOfRegistrationRect()
#     widget.resize(640, 480)
#     widget.show()
#     sys.exit(app.exec_())