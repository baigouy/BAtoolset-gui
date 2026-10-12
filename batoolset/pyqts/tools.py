from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from qtpy.QtGui import QPainter,QTransform,QImage,QPolygonF,QFont, QTextDocument,QColor,QPolygon,QPixmap
from qtpy.QtCore import QRectF, QPointF, QSize, QRect, QPoint
from qtpy.QtCore import Qt, QObject, QEvent
from qtpy.QtWidgets import QHBoxLayout, QSlider,QLabel,QComboBox,QSpinBox,QWidget,QScrollArea,QDoubleSpinBox
import math
import numpy as np
import sys

# class WheelFilter(QObject):
#     def eventFilter(self, obj, event):
#         if event.type() == QEvent.Wheel:
#             if isinstance(obj, (QComboBox, QSpinBox)):
#                 return True
#         return super().eventFilter(obj, event)
#
#
# def disable_wheel_for_widget_and_children(widget):
#     wheel_filter = WheelFilter(widget)
#     widget.installEventFilter(wheel_filter)
#
#     for child in widget.findChildren(QWidget):
#         if isinstance(child, (QComboBox, QSpinBox)):
#             child.installEventFilter(wheel_filter)
#         elif not isinstance(child, QScrollArea):
#             child.installEventFilter(wheel_filter)
#             disable_wheel_for_widget_and_children(child)

# def disable_wheel_for_combo_and_spin(app):
#     app.setStyleSheet("""
#         QComboBox, QSpinBox, QDoubleSpinBox {
#             qproperty-wheelEnabled: false;
#         }
#     """)

# class WheelBlocker(QObject):
#     def eventFilter(self, obj, event):
#         if event.type() == QEvent.Wheel:
#             return isinstance(obj, (QComboBox, QSpinBox, QDoubleSpinBox))
#         return False
#
# def disable_wheel_for_combo_and_spin(app):
#     blocker = WheelBlocker(app)
#     app.installEventFilter(blocker)

def createPixmapFromLUT(lut, height=16, length=256, orientation='horizontal'):
    """
    Creates a QPixmap from the LUT with the specified orientation and dimensions.

    :param lut: List of color values in the LUT.
    :param height: The height of the LUT preview.
    :param length: The length of the preview (number of colors).
    :param orientation: The orientation of the LUT ('horizontal' or 'vertical').
    :return: QPixmap representing the LUT.
    """
    image = QImage(256, height, QImage.Format_RGB32)

    for i in range(256):
        if isinstance(lut[i], str):
            # If lut[i] is a string, convert it to QColor
            color = QColor(lut[i])
        elif isinstance(lut[i], (list, np.ndarray)) and len(lut[i]) == 3:
            # If lut[i] is an RGB array, convert it to QColor
            color = QColor(int(lut[i][0]), int(lut[i][1]), int(lut[i][2]))
        else:
            raise ValueError("LUT entry must be a color string or an RGB array")

        for j in range(height):
            image.setPixelColor(i, j, color)

    pixmap = QPixmap.fromImage(image)
    scaled_pixmap = pixmap.scaled(length, height, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

    if orientation != 'horizontal':
        # Rotate the scaled pixmap 90 degrees clockwise for vertical orientation
        transform = QTransform().rotate(90)
        scaled_pixmap = scaled_pixmap.transformed(transform)

    return scaled_pixmap

def calculate_dpi_for_pixel_thickness(linewidth_pt, desired_pixel_thickness):
    """
    Calculate the DPI needed to achieve a specific line thickness in pixels.

    :param linewidth_pt: The linewidth in points (as used in matplotlib)
    :param desired_pixel_thickness: The desired line thickness in pixels in the final image
    :return: The calculated DPI
    """
    dpi = (desired_pixel_thickness * 72) / linewidth_pt
    return round(dpi)

def setPixmapToLabel(pixmap, label):
    """
    Sets the given QPixmap to the provided QLabel.

    :param pixmap: QPixmap to set on the label.
    :param label: QLabel to display the pixmap.
    """
    label.setPixmap(pixmap)

def updateLutLabelPreview(lut, previewLabel, length, orientation='horizontal', height=16):
    """
    Updates the preview label with an image representing the LUT.

    :param lut: List of color values in the LUT.
    :param previewLabel: The QLabel where the preview image will be displayed.
    :param length: The total length of the preview, including buttons and spacing.
    :param orientation: The orientation of the LUT ('horizontal' or 'vertical').
    """
    pixmap = createPixmapFromLUT(lut, height=height, length=length, orientation=orientation)
    setPixmapToLabel(pixmap,previewLabel)


def getCtrlModifierAsString():
    import sys
    if sys.platform == "darwin":
        return "Meta"  # Command key on macOS
    # else:
    return "Ctrl"  # Control key on other platforms


def getCtrlModifier():
    if sys.platform == "darwin":
        return Qt.MetaModifier
    else:
        return Qt.ControlModifier

class WheelBlocker(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            return isinstance(obj, (QComboBox, QSpinBox, QDoubleSpinBox))
        return False


def disable_wheel_for_combo_and_spin(widget):
    blocker = WheelBlocker(widget)
    widget.installEventFilter(blocker)

    for child in widget.findChildren(QWidget):
        child.installEventFilter(blocker)

# return true if antialiasing is on
def check_antialiasing(painter):
    # print('testing antialias', painter.testRenderHint(QPainter.Antialiasing))
    return painter.testRenderHint(QPainter.Antialiasing)

def get_items_of_combo(combo_box):
    items = [combo_box.itemText(i) for i in range(combo_box.count())]
    return items

def get_painter_transform_and_rotation(painter):
    # Get the current transformation matrix
    transform = painter.transform()

    # Get the rotation angle from the transformation matrix
    rotation_angle = math.atan2(transform.m12(), transform.m11()) * 180 / math.pi

    return transform, rotation_angle

def copy_transform_without_rotation(current_transform):
    # Extract the components from the current transform
    m11 = current_transform.m11()  # Horizontal scaling
    m12 = current_transform.m12()  # Vertical shearing
    m13 = current_transform.m13()  # Horizontal projection (should be 0 for affine transforms)
    m21 = current_transform.m21()  # Horizontal shearing
    m22 = current_transform.m22()  # Vertical scaling
    m23 = current_transform.m23()  # Vertical projection (should be 0 for affine transforms)
    m31 = current_transform.m31()  # Horizontal translation
    m32 = current_transform.m32()  # Vertical translation
    m33 = current_transform.m33()  # Additional scaling factor (usually 1 for affine transforms)

    # Create a new transform without the rotation
    new_transform = QTransform(m11, 0, m13,
                               0, m22, m23,
                               m31, m32, m33)

    return new_transform


def copy_scale_only(current_transform):
    # Extract the scale components from the current transform
    m11 = current_transform.m11()  # Horizontal scaling
    m22 = current_transform.m22()  # Vertical scaling

    # Create a new transform with only the scaling components
    new_transform = QTransform(m11, 0, 0,
                               0, m22, 0,
                               0, 0, 1)

    return new_transform


def copy_scale_and_translation_only(current_transform):
    # Extract the scale components from the current transform
    m11 = current_transform.m11()  # Horizontal scaling
    m22 = current_transform.m22()  # Vertical scaling

    # Extract the translation components from the current transform
    m31 = current_transform.m31()  # Horizontal translation
    m32 = current_transform.m32()  # Vertical translation

    # Create a new transform with only the scaling and translation components
    new_transform = QTransform(m11, 0, 0,
                               0, m22, 0,
                               m31, m32, 1)

    return new_transform

def rotate_image(image, angle, parent_painter=None, annotations=None,__DEBUG__=False):
    # Get the dimensions of the original image
    width, height = image.width(), image.height()
    # print('inside', width, height, angle)

    # Define the initial rectangle
    init_rect = QRectF(0, 0, width, height)
    center = init_rect.center()

    # Create the transformation for rotating the image
    transformation_for_image = QTransform()
    transformation_for_image.translate(center.x(), center.y())
    transformation_for_image.rotate(angle)
    transformation_for_image.translate(-center.x(), -center.y())

    # Map the initial rectangle to the rotated polygon
    rotated_polygon = transformation_for_image.mapToPolygon(init_rect.toRect())
    rotated_rect = QRectF(rotated_polygon.boundingRect())

    # try:
    #     print('rotated_rect', rotated_rect.size(), rotated_rect, 'angle', angle, 'init', init_rect)
    # except:
    #     print('rotated_rect', rotated_rect.size(), rotated_rect, 'angle', angle)

    # Create a new QImage with the dimensions of the rotated rectangle
    rotated_image = QImage(int(rotated_rect.width()), int(rotated_rect.height()), QImage.Format_ARGB32_Premultiplied)
    rotated_image.fill(Qt.transparent)

    # Create a QPainter to draw the rotated image
    painter2 = QPainter(rotated_image)
    if parent_painter:
        painter2.setRenderHint(parent_painter.renderHints())
    else:
        # print('removing antialisaing')
        # painter2.setRenderHint(QPainter.Antialiasing, False)
        painter2.setRenderHint(QPainter.Antialiasing, True) # just for now

    if __DEBUG__:
        pass # TODO -−> set a pen and plot the rects

    # Calculate the offset to center the rotated image
    offset = QPointF((rotated_rect.width() - width) / 2, (rotated_rect.height() - height) / 2)


    # print('offset inside dabula', offset)

    # Translate the painter to the calculated offset
    painter2.translate(offset)

    # Apply the rotation transformation
    painter2.translate(center.x(), center.y())
    painter2.rotate(angle)
    painter2.translate(-center.x(), -center.y())



    # Draw the original image onto the rotated image
    painter2.drawImage(init_rect, image, init_rect)

    if annotations:
        for elm in annotations:
            if hasattr(elm, 'placement'):
                if elm.placement is not None:
                    if not elm.placement.position_to_string():
                    #     continue
                    # else:
                        continue


            try:
                    painter2.save()
                    elm.draw(painter2)
                    painter2.restore()
            except:
                pass

    # then draw all annotations



    painter2.end()

    # Save the rotated image for verification
    # rotated_image.save('/home/aigouy/Bureau/test.png')

    return rotated_image

def crop_image(image: QImage, crop_left: int, crop_right: int, crop_top: int,  crop_bottom: int) -> QImage:
    """
    Crops the given QImage object by the specified amount of pixels on each side.

    Args:
        image: The QImage object to crop.
        crop_left: The number of pixels to crop from the left side.
        crop_top: The number of pixels to crop from the top side.
        crop_right: The number of pixels to crop from the right side.
        crop_bottom: The number of pixels to crop from the bottom side.

    Returns:
        A new QImage object with the cropped image.
    """
    if not crop_left:
        crop_left=0
    if not crop_right:
        crop_right=0
    if not crop_top:
        crop_top=0
    if not crop_bottom:
        crop_bottom=0

    # Calculate the position and dimensions of the cropped image
    x = int(crop_left)
    y = int(crop_top)
    width = int(image.width() - crop_left - crop_right)
    height = int(image.height() - crop_top - crop_bottom)

    # Create a QRect object with the position and dimensions of the cropped image
    rect = QRect(x, y, width, height)

    # Create a new QImage object with the cropped image
    cropped_image = image.copy(rect)

    return cropped_image


def tst_translation(rect: QRectF, angle: float, crop_left: float, crop_right: float, crop_top: float, crop_bottom: float) -> QPolygonF:
    rotated_shape = get_shape_after_rotation_and_crop(rect, angle, crop_left, crop_right, crop_top, crop_bottom)
    return rect.center()-get_centroid(rotated_shape)


def get_shape_after_rotation_and_crop(rect, angle, crop_left, crop_right, crop_top, crop_bottom, return_AR = False):
    # this retruns the qrectf corresponding to the initial image after rotation and crop --> what will be displayed --> that seems to work fine --> TODO



    if not angle and not crop_left and not crop_right and not crop_top and not crop_bottom:
        # print('NADA FOUND --> cancelling')
        if return_AR:
            return rect.width()/rect.height(), None

        return None

    if True:
        # maybe this should be an option
        # rect.setX(0)
        # rect.setY(0)
        rect = QRectF(0,0,rect.width(), rect.height())

    # assume all is at 0 -->

    # Calculate the center of the rectangle
    center = rect.center()

    # Create a transformation matrix to rotate the rectangle around its center
    transform = QTransform()
    if angle:
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        transform.translate(-center.x(), -center.y())

    # Apply the transformation to the rectangle
    # bounding_rect = transform.mapRect(rect)
    rotated_rect_as_polygon = transform.mapToPolygon(rect.toRect())

    # Calculate the bounding rectangle of the rotated rectangle

    bounds_rotated = rotated_rect_as_polygon.boundingRect()

    # print(bounds_rotated)

    bounds_rotated.setLeft(int(bounds_rotated.left()+crop_left))
    bounds_rotated.setRight(int(bounds_rotated.right()-crop_right))
    bounds_rotated.setTop(int(bounds_rotated.top()+crop_top))
    bounds_rotated.setBottom(int(bounds_rotated.bottom()-crop_bottom))


    # this is what should be used to get AR !!! ---> TODO
    # print('AR in the bidule', bounds_rotated.width()/bounds_rotated.height())





    # this gives me a rect that I can plot back on the orig that will show what is displayed -->

    # no in fact I need to get the union of the yellow rotated poly/rect and the blue --> TODO

    # Get the overlapping area between the polygon and the rectangle
    transform = QTransform()
    crop_rect_as_polygon = transform.mapToPolygon(bounds_rotated)

    # print(crop_rect_as_polygon.boundingRect()) # c'est le bounding rect difference --> -23 --> see why that is ???

    overlapping_polygon = rotated_rect_as_polygon.intersected(crop_rect_as_polygon)
    # print(overlapping_polygon.boundingRect())

    # overlapping_polygon_f = QPolygonF(overlapping_polygon)
    transform = QTransform()
    # --> all good --> I have it now see how I can plot it back onto the original --> see the translation and rotation I need to apply
    # transform.translate(bounds_rotated.center().x(),bounds_rotated.center().y())
    # transform.rotate(-angle)
    # transform.translate(-bounds_rotated.center().x(), -bounds_rotated.center().y())

    # we revert to initial rotation !!!
    if angle:
        transform.translate(center.x(),center.y()) #
        transform.rotate(-angle)
        transform.translate(-center.x(), -center.y())
    # overlapping_polygon_rotated = overlapping_polygon_f.transformed(transform)
    overlapping_polygon_rotated = transform.map(overlapping_polygon)

    # print(overlapping_polygon_rotated.boundingRect())
    # print()
    if not return_AR:
        return overlapping_polygon_rotated
    else:
        return bounds_rotated.width()/bounds_rotated.height(), overlapping_polygon_rotated

def get_original_shape_from_rect_and_angle(parent_rect, drawn_rect, angle):
    # that works perfect for shapes below 90 degrees --> see how to fix that
    # Calculate the bounding rectangle of the rotated rectangle
    drawn_rect = drawn_rect.normalized()

    center = parent_rect.center()
    # the mapped rect will have the same centroid position as the polygon and as the rect by the way or as the
    transform = QTransform()
    transform.translate(center.x(), center.y())
    transform.rotate(-angle)
    transform.translate(-center.x(), -center.y())

    # get the transformed shape
    rotated_back_drawn = transform.mapToPolygon(drawn_rect.toRect())
    rotated_back_parent = transform.mapToPolygon(parent_rect.toRect())

    # if I have the position of the centroid I can place any rect on top
    drawn_rect.translate(QPointF(rotated_back_drawn.boundingRect().center())-drawn_rect.center())

    crop_left = -(rotated_back_parent.boundingRect().left()-drawn_rect.left())
    crop_right = rotated_back_parent.boundingRect().right()-drawn_rect.right()
    crop_top = -(rotated_back_parent.boundingRect().top() - drawn_rect.top())
    crop_bottom = rotated_back_parent.boundingRect().bottom()-drawn_rect.bottom()

    if True: # maybe put this as a parameter
        crop_left = int(crop_left)
        crop_right = int(crop_right)
        crop_top = int(crop_top)
        crop_bottom = int(crop_bottom)

    return -angle, crop_left, crop_right, crop_top, crop_bottom

def get_html_text_with_font(text, font):
    # Create a font
    # font = QFont()
    # font.setFamily(font_family)
    # font.setPointSize(font_size)
    # font.setWeight(QFont.Normal if font_style == 'Normal' else QFont.Bold)

    # Create a QTextDocument object
    text_document = QTextDocument()

    # Apply the font to the text document
    text_document.setDefaultFont(font)

    # Set the text
    text_document.setHtml('<p>' + text + '</p>')

    # Get the HTML equivalent with the applied font
    html_text = text_document.toHtml()

    return html_text

def get_centroid(polygon: QPolygonF) -> QPointF:
    # Ensure the polygon is closed
    if polygon.isEmpty():
        return QPointF()

    if polygon.first() != polygon.last():
        polygon.append(polygon.first())

    n = len(polygon)
    A = 0  # Partial area
    Cx = 0  # x coordinate of centroid
    Cy = 0  # y coordinate of centroid

    for i in range(n - 1):
        x0, y0 = polygon[i].x(), polygon[i].y()
        x1, y1 = polygon[i + 1].x(), polygon[i + 1].y()
        cross_product = x0 * y1 - x1 * y0
        A += cross_product
        Cx += (x0 + x1) * cross_product
        Cy += (y0 + y1) * cross_product

    A /= 2
    Cx /= (6 * A)
    Cy /= (6 * A)

    return QPointF(Cx, Cy)
# def get_centroid2(polygon):
#     """
#     Returns the centroid (center of mass) of a QPolygonF object.
#     """
#     area = 0.0
#     centroid = QPointF(0.0, 0.0)
#
#     # Calculate the signed area and centroid using the Shoelace formula
#     for i in range(len(polygon)):
#         j = (i + 1) % len(polygon)
#         a = polygon[i].x() * polygon[j].y() - polygon[j].x() * polygon[i].y()
#         area += a
#         centroid += QPointF((polygon[i].x() + polygon[j].x()) * a, (polygon[i].y() + polygon[j].y()) * a)
#
#     area *= 0.5
#     if area != 0.0:
#         centroid /= (3.0 * area)
#
#     return centroid

# def get_centroid(qpolygonf):
#     x_sum = 0
#     y_sum = 0
#     num_points = qpolygonf.count()-1 # assume the shape is closed so the last point is the first and we should take it only once
#
#     for i in range(num_points):
#         point = qpolygonf.at(i)
#         x_sum += point.x()
#         y_sum += point.y()
#
#     centroid_x = x_sum / num_points
#     centroid_y = y_sum / num_points
#
#     return QPointF(centroid_x, centroid_y)
def grab_n_find_color(qwidget, color=QColor(0, 0, 0)):
    # Capture the contents of the widget as a QPixmap object
    first_black_pixel = None
    pixmap = qwidget.grab()
    # Find the coordinates of the first black pixel
    width = pixmap.width()
    height = pixmap.height()
    image = pixmap.toImage()
    for x in range(width):
        for y in range(height):
            cur_col = image.pixelColor(x, y)
            if cur_col == color:
                first_black_pixel = (x, y)
                print(first_black_pixel) # --> 15,89 --> ok -−> do a fix then but ok for now
                break
        else:
            continue
        break
    del pixmap
    del image
    return first_black_pixel

def average_polygons(*polygons):
    """
    Calculate the average of the QPolygonF objects.

    Args:
        *polygons: A variable number of QPolygonF objects.

    Returns:
        QPolygonF: The average of the QPolygonF objects.
    """
    if not polygons:
        return QPolygon()

    # Check that all polygons have the same number of points
    num_points = len(polygons[0])
    for polygon in polygons[1:]:
        if len(polygon) != num_points:
            raise ValueError("All polygons must have the same number of points.")


    out = QPolygon()
    # Calculate the average of the x and y coordinates of each point
    # average_points = []
    for i in range(num_points):
        x_sum = 0
        y_sum = 0
        for polygon in polygons:
            x_sum += polygon[i].x()
            y_sum += polygon[i].y()
        x_avg = x_sum / len(polygons)
        y_avg = y_sum / len(polygons)
        # average_points.append(QPointF(x_avg, y_avg))
        out.append(QPoint(int(x_avg), int(y_avg)))
    return out


def create_dim_slider(dimension=None, max_dim=1, return_slider=True):
    dim_slider_with_label1 = QHBoxLayout()
    label_slider1 = QLabel()
    if dimension is not None:
        label_slider1.setText(dimension)
    dim_slider = QSlider(Qt.Horizontal)
    dim_slider.setMinimum(0)
    dim_slider.setMaximum(max_dim-1)
    dim_slider_with_label1.addWidget(label_slider1)
    dim_slider_with_label1.addWidget(dim_slider)
    dim_slider.setObjectName(dimension)
    if not return_slider:
        return dim_slider_with_label1
    else:
        return dim_slider_with_label1, dim_slider

# def empty_widget_layout(widget):
#     if widget is None:
#         return
#     layout = widget.layout()
#     if not layout:
#         return
#     while layout.count():
#         item = layout.takeAt(0)
#         widget = item.widget()
#         # Delete the widget associated with the item
#         if widget is not None:
#             widget.setParent(None)
#             widget.deleteLater()
#         # else:
#         #     print('weirdo stuff',item)
#         #     layout =  item.layout()
#         # Delete the item
#         # del item
#     # return layout

def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        if item.widget() is not None:
            item.widget().deleteLater()
        else:
            clear_layout(item.layout())


def distance(point1, point2):
    """
    Compute the Euclidean distance between two points.

    Parameters:
        point1 (QPointF): First point
        point2 (QPointF): Second point

    Returns:
        float: Euclidean distance between the two points
    """
    dx = point1.x() - point2.x()
    dy = point1.y() - point2.y()
    return math.sqrt(dx * dx + dy * dy)

def select_in_combobox(combobox, text=None,value=None, default_index_on_not_found=None):
    if text is None and value is None:
        print('Error text or value must be specified!!!')

    if value is not None:
        index = combobox.findVale(value)
    elif text is not None:
        index = combobox.findText(text)
    if index >= 0:
        combobox.setCurrentIndex(index)
    else:
        if default_index_on_not_found is not None:
            combobox.setCurrentIndex(default_index_on_not_found)

def find_action_by_text(menu, text='ignore'):
    for action in menu.actions():
        if action.text() == text:
            return action
    return None


if __name__ == '__main__':
    import sys

    if False:
        from PyQt6.QtCore import QPointF, QRectF

        # Define the two sets of rectangles
        rects1 = [
            QRectF(0.0, 0.0, 145.0, 303.0),
            QRectF(0.0, 0.0, 205.20137371117733, 428.80011196197745),
            QRectF(0.0, 0.0, 205.20137371117733, 428.80011196197745)
        ]
        rects2 = [
            QRectF(0.0, 0.0, 145.0, 303.0),
            QRectF(0.0, 0.0, 106.1386415747469, 230.67464768911657),
            QRectF(0.0, 0.0, 342.47401681451663, 260.3934673300457)
        ]

        point = rects1[-1].center()-rects2[-1].center()
        print(point)
        print(rects2[-1].translated(point.x(), point.y()))

        # Define the desired overall translation
        desired_translation = QPointF(50, -50)

        # Calculate the center of each rectangle
        centers1 = [rect.center() for rect in rects1]
        centers2 = [rect.center() for rect in rects2]

        print('centers1',centers1)
        print('centers2',centers2)

        # Calculate the translations required to move the centers of the rectangles in the first set to the centers of the rectangles in the second set
        translations = [centers2[i] - centers1[i] for i in range(len(rects1))]

        # Calculate the average of the translations
        average_translation = QPointF(sum(t.x() for t in translations) / len(translations),
                                      sum(t.y() for t in translations) / len(translations))

        # If the average translation is not equal to the desired translation, adjust the individual translations
        if average_translation != desired_translation:
        # Calculate the difference between the average translation and the desired translation
            diff = desired_translation - average_translation

            # Adjust the individual translations
            adjusted_translations = [t + diff for t in translations]

            # Use the adjusted translations to move the rectangles in the first set to the second set
            moved_rects = [rect.translated(t) for rect, t in zip(rects1, adjusted_translations)]
        else:
            # Use the original translations to move the rectangles in the first set to the second set
            moved_rects = [rect.translated(t) for rect, t in zip(rects1, translations)]

        print(translations)
        print(average_translation)

        sys.exit(0)

    if True:
        # get_shape_after_rotation_and_crop(QRectF(0,0,145,303), 42, 30,40,60,80)
        print(get_shape_after_rotation_and_crop(QRectF(0,0,145,303), 42, 30,40,60,80))
        print(tst_translation(QRectF(0,0,145,303), 42, 30,40,60,80))
        # print(get_shape_after_rotation_and_crop(QRectF(0, 0, 145, 303), 42, 60, 30, 0, 0))
        # print(tst_translation(QRectF(0,0,145,303), 42, 60,30,0,0))

        print(get_centroid(get_shape_after_rotation_and_crop(QRectF(0,0,145,303), 42, 30,40,60,80)))



        sys.exit(0)

    if True:
        # rotation of images 1 and 2 are correct so the error is clearly elsewhere if not centered -−> see why that is
        image = QImage('/E/Sample_images/counter/01.png')
        # image = QImage('/E/Sample_images/counter/02.png')
        # image = QImage('/E/Sample_images/sample_images_PA/test.png')
        rotated =  rotate_image(image, 42)
        rotated.save('/home/aigouy/Bureau/test.png')


        sys.exit(0)
