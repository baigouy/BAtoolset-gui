from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from qtpy.QtGui import QTransform,QPen, QColor
from qtpy.QtCore import QPointF
from batoolset.figure.alignment import pack2, align2, align_positions
from batoolset.drawings.shapes.rectangle2d import Rectangle2D
from batoolset.drawings.shapes.txt2d import TAText2D
from batoolset.drawings.shapes.Position import Position
# logger
from batoolset.tools.logger import TA_logger

logger = TA_logger()

class ScaleBar(Rectangle2D):

    # TODO need a scaling factor for the bar if image is itself scaled or ??? --> most likely yes need think about it
    # TODO handle bar color
    def __init__(self, bar_width_in_units=0, legend="", unit_to_pixel_conversion_factor=1, bar_height_in_px=3, placement=Position('bottom-right'), bar_color=None, __version__=1.0,**kwargs):
        super(ScaleBar, self).__init__()
        # print('unsupported inputs scale',kwargs)
        self.scale = 1
        # colour of the bar itself (0xRRGGBB); None = white. A dedicated field:
        # the inherited `color` was never used for drawing, and old files hold
        # stale values there (e.g. yellow) that must not suddenly show up.
        self.bar_color = bar_color
        self.bar = Rectangle2D(color=None, fill_color=0xFFFFFF if bar_color is None else bar_color, stroke=0)
        self.extra_space = 3
        # print('bar_width_in_units',bar_width_in_units, 'unit_to_pixel_conversion_factor',unit_to_pixel_conversion_factor)

        self.bar_height_in_px = bar_height_in_px
        self.bar.setWidth(bar_width_in_units / (unit_to_pixel_conversion_factor if unit_to_pixel_conversion_factor else 1))
        self.bar.setHeight(self.bar_height_in_px)
        self.legend = None
        self.setLegend(legend)

        # print('self.legend inside',self.legend)

        self.bar_width_in_units = bar_width_in_units
        self.unit_to_pixel_conversion_factor = unit_to_pixel_conversion_factor
        if not isinstance(placement, Position):
            placement = Position(placement)
        self.placement = placement
        self.line_style = None # useless but require for compat with other shapes
        self.__version__ = __version__

    def setLegend(self, legend):
        if isinstance(legend, str):
            self.legend = TAText2D(legend)
        elif isinstance(legend, TAText2D):
            self.legend = legend
        else:
            self.legend = None

    def setBarWidth(self, bar_width_in_units):
        self.bar_width_in_units = bar_width_in_units
        self.bar.setWidth(bar_width_in_units / (self.unit_to_pixel_conversion_factor if self.unit_to_pixel_conversion_factor else 1)) # this is ok but this is unscaled!!!
        self.updateBoudingRect()

    def update_bar_at_scale(self,scale):
        # pass
        # print('bar_width_in_units', self.bar_width_in_units,  self.unit_to_pixel_conversion_factor, scale, self.bar.width(), self.width())
        #
        # self.bar.setWidth((self.bar_width_in_units * self.unit_to_pixel_conversion_factor) /scale)
        #
        # print('after', self.bar.width(), self.width()) # --> bar width is computed correctly so why isn't the size ok !!!

        self.scale = scale

        self.bar.setWidth((self.bar_width_in_units / (self.unit_to_pixel_conversion_factor if self.unit_to_pixel_conversion_factor else 1.)) / self.scale)

        # self.packY() # it is the packing that fucks it all
        # print('after2a', self.bar.width(),self.width())  # --> bar width is computed correctly so why isn't the size ok !!!
        self.updateBoudingRect()
        # print('after2b', self.bar.width(),self.width())  # --> bar width is computed correctly so why isn't the size ok !!!

        # weird bug is here --> it resets the scale --> not what I want

        # print('after2', self.bar.width(), self.width())  # --> bar width is computed correctly so why isn't the size ok !!!



    def width(self, *args, **kwargs):
        return super().width() # mandatory for proper scaling KEEP

    def height(self, *args, **kwargs):
        return super().height() # mandatory for proper scaling KEEP

    def setConversionFactor(self, unit_to_pixel_conversion_factor):
        self.unit_to_pixel_conversion_factor = unit_to_pixel_conversion_factor

    def draw(self, painter, draw=True, parent=None):

        # shall I reset scale from painter --> maybe
        # painter.setWorldTransform(QTransform())
        # I need reset scale from painter as it is handled directly in the object
        # then position is not ok but why

        painter.save()



        # we dynamically place the bar with respect to the bounding rect
        self.bar.moveCenter(self.center())
        self.bar.moveBottom(self.bottom() - self.extra_space)
        bar_color = getattr(self, 'bar_color', None)
        self.bar.fill_color = 0xFFFFFF if bar_color is None else bar_color
        self.bar.draw(painter=painter)
        if self.legend is not None:
            # we dynamically place the legend above the bar, inside the bounding rect
            self.legend.moveCenter(self.center())
            self.legend.moveTop(self.top() + self.extra_space / 2.)
            self.legend.draw(painter=painter)
        # self.drawAndFill(painter=painter)

        # the bar should be centered on


        if False: # just for debug !!!
            painter.setPen(QPen(QColor("Green"),3))
            painter.drawRect(self) # --> definitely the rect is incorrect -−> the error is in the placement of the rect

        painter.restore()
    def updateBoudingRect(self):
        """
        updates the image bounding rect depending on content
        :return:
        """

        # contient deux objects et est donc la somme des deux
        # --> facile en theorie faire que du packing et de l'alignement à gauche droite ou ailleurs
        # pack in y direction the text and the bar
        extra_space_below = 3 # TODO see how to make it not stuck to the bottom of the image --> it needs be a specificity of the bar and text but not for images --> TODO -> see how to do that
        x = self.x()
        y = self.y()
        # x2 = None
        # y2 = None
        w=None
        h=None
        # the pb is that the shapes are not properly placed with respect to that
        # and if the rect position is properly placed it is reset by wro,g placement of inner objects

        # x=self.topLeft().x()
        # y=self.topLeft().y()

        to_pack = [self.bar, self.legend]
        for img in to_pack:
            if img is None:
                continue
            if not w:
                w = img.width()
            if not h:
                h = img.height()

            try:
                w = max(w, img.width())
            except Exception:
                pass
            # h = max(h, img.height())

            # try:
            #     topLeft = img.topLeft()
            #     if x is None:
            #         x = topLeft.x()
            #     if y is None:
            #         y = topLeft.y()
            #     x = min(topLeft.x(), x)
            #     y = min(topLeft.y(), y)
            #
            #     # print(img, img.boundingRect(), type(img))
            #     # print(img, img.boundingRect(), type(img), img.boundingRect().height())
            #
            #     if x2 is None:
            #         x2 = topLeft.x() + img.boundingRect().width()
            #     if y2 is None:
            #         y2 = topLeft.y() + img.boundingRect().height()
            #     x2 = max(topLeft.x() + img.boundingRect().width(), x2)
            #     y2 = max(topLeft.y() + img.boundingRect().height(), y2)
            # except:
            #     pass

        h = self.bar.height()
        if self.legend and not isinstance(self.legend, str):
            h += self.legend.height()  # stack bar and legend vertically

        # shall I translate the stuff at the same time ??? -−> maybe



        if False:
            self.setX(x-self.extra_space)
            self.setY(y-self.extra_space)
            self.setWidth(x2 - x)
            # if not self.legend or self.width()<=self.bar.width():
            self.setWidth(self.width()+self.extra_space*2) # maybe
            self.setHeight(y2 - y)
            # self.setHeight(self.height()+3) # add extra
            self.setHeight(self.height()+self.extra_space*2)

        self.setWidth(w+2*self.extra_space)
        self.setHeight(h+2*self.extra_space)

        # MEGA TOOD -> maybe I should only add space or not depending on placement -> check that !!!



    def packY(self, space=3):
        # center in vertical axis then pack
        #
        # last_x = 0
        # last_y = 0
        #
        # to_pack = [self.bar, self.legend]
        # for i in range(len(to_pack)):
        #     img = self.images[i]
        #     if i != 0:
        #         last_y += space
        #     img.setTopLeft(img.topLeft().x(), last_y)
        #     # get all the bounding boxes and pack them with desired space in between
        #     # get first point and last point in x
        #     x = img.boundingRect().x()
        #     y = img.boundingRect().y()
        #     last_x = img.boundingRect().x() + img.boundingRect().width()
        #     last_y = img.boundingRect().y() + img.boundingRect().height()
        if self.legend is not None and not isinstance(self.legend, str):
            self.bar.setWidth((self.bar_width_in_units / self.unit_to_pixel_conversion_factor)/self.scale)
            # alignCenterH(self.legend, self.bar)
            align2(align_positions[-1], self.legend, self.bar)
            # align_positions = ['Top', 'Bottom', 'Left', 'Right', 'CenterV', 'CenterH']
            # packY(12, self.legend, self.bar)
            pack2(3, ('-' if self.placement.check_position('top') else '') + 'Y', False, *[self.legend, self.bar])



        self.updateBoudingRect()





    # finally just need align right

    # def setTopLeft(self, *args):
    def setTopLeft(self, *args):
        curP1 = self.topLeft()
        if args:
            if len(args) == 1:
                # assume a QpointF
                super().moveTopLeft(args[0])
            elif len(args) == 2:
                super().moveTopLeft(QPointF(args[0], args[1]))
            else:
                logger.error('invalid args for top left')

        newP1 = self.topLeft()
        # if
        # # self.setTopLeft(*args)
        # current_pos = self.boundingRect().topLeft()
        # self.translate(point.x() - current_pos.x(), point.y() - current_pos.y())


        if False:
            # TODO check this code as most of this si probably totally useless
            # curP1 = self.topLeft()
            self.packY()
            # Rectangle2D.setTopLeft(self, *args)
            # Rectangle2D.setTopLeft(self, *args)
            # newP1 = self.topLeft()

            to_pack = [self.bar, self.legend]
            for img in to_pack:
                if img is not None:
                    img.translate(newP1.x() - curP1.x(), newP1.y() - curP1.y())
                    # img.translate(self.center().x()-img.center().x(),0)

        # print('before aazezae', self.getRect())


        self.updateBoudingRect()
        # print('after qsdqsdqd', self.getRect())

    # def set_to_scale(self, scale):
    #     self.scale = scale

    # def setcolor

    # get the bounds of the bar with the associated text
    # center text on bar see how I do in EZF

    def __repr__(self):
        class_name = type(self).__name__
        memory_address = hex(id(self))
        return f"{class_name}-{memory_address}"


    # def to_dict(self):
    #     x = self.x()
    #     y = self.y()
    #     width = self.width()
    #     height = self.height()
    #
    #     # Create a dictionary representation of the values of the super object
    #     output_dict = {
    #         'x': x,
    #         'y': y,
    #         'width': width,
    #         'height': height,
    #     }
    #     # Update the dictionary with the __dict__ of Rectangle2D
    #     output_dict.update(self.__dict__)
    #     return output_dict