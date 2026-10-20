# this seems to work better and better !!!
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
import matplotlib.pyplot as plt
import numpy as np
# from batoolset.drawings.shapes.vectorgraphics2d import VectorGraphics2D
from batoolset.img import Img
from batoolset.lists.tools import move_left, move_right, is_iterable
import random
import sys
import traceback
# this will replace cols or rows and will be able to do both but more flexibly
from timeit import default_timer as timer
from batoolset.serializations.tools import create_objects_from_dict
from batoolset.drawings.shapes.image2d import Image2D
from batoolset.drawings.shapes.rectangle2d import Rectangle2D
from batoolset.drawings.shapes.txt2d import TAText2D
from qtpy.QtCore import QRectF, QSizeF,QPointF
from qtpy.QtWidgets import QApplication
from qtpy.QtGui import QPainter, QColor, QBrush, QPen, QTransform
from batoolset.figure.alignment import pack2, align2, align_positions
from batoolset.tests.tools import are_ratios_almost_equal
from batoolset.drawings.shapes.compute_optimal_size_all_merged import resize_rects_within_total_width, \
    resize_rects_within_total_height

ORIENTATIONS = ["X","Y"] #,"grid"

def get_all_contained_images(obj):
    """
    Returns a list of all iterable elements in the given object.
    """
    # print(is_iterable(obj), obj)
    if is_iterable(obj):
        # obj is an iterable, so iterate over its elements
        elements = []
        for element in obj:
            elements.extend(get_all_contained_images(element))
        # if not elements:
        #     return None
        return elements
    else:
        # obj is not an iterable, so return an empty list
        return [obj]
    # if not inner_elements:
    #     return None


# def get_imprecision2(grp, desired_size):
#     if grp.orientation == 'X':
        # take the first immutable stuff
def get_iterable_elements(obj):
    """
    Returns a list of all iterable elements in the given object.
    """

    # print(is_iterable(obj), obj)
    if is_iterable(obj):
        # obj is an iterable, so iterate over its elements
        elements = [obj]
        for element in obj:
            elements.extend(get_iterable_elements(element))
        # if not elements:
        #     return None
        return elements
    else:
        # obj is not an iterable, so return an empty list
        return []


def get_parent_of_obj(obj, shapes_to_draw):
    if not shapes_to_draw:
        return
    if not isinstance(shapes_to_draw, list):
        shapes_to_draw=[shapes_to_draw]

    for shape in shapes_to_draw:
        iterables = get_iterable_elements(shape)
        if iterables:
            for itr in iterables:
                if obj in itr:
                    return itr


# def get_imprecision(grp, desired_size=None):
#     # first = grp[0]
#     # last = grp[-1]
#
#     # print('first.immutable',first.immutable, last.immutable)
#     #
#     # if first.immutable:
#     #     for elm in grp:
#     #         if not elm.immutable:
#     #             first=elm
#     #             break
#     # if last.immutable:
#     #     for elm in grp[::-1]:
#     #         if not elm.immutable:
#     #             last=elm
#     #             break
#     #
#     # print('first',first, grp.content[1]) -−> indeed I cannot use that
#
#     # imprecisionX = abs(first.getRect().height() - last.getRect().height())
#     # imprecisionY = abs(first.getRect().width() - last.getRect().width())
#     # imprecision = min(abs(imprecisionX), abs(imprecisionY))
#     if desired_size:
#         imprecisionX = abs(grp.getRect().height() - desired_size)
#         imprecisionY = abs(grp.getRect().width() -desired_size)
#     else:
#         imprecisionX = abs(grp.getRect().height() - int(round(grp.getRect().height())))
#         imprecisionY = abs(grp.getRect().width() - int(round(grp.getRect().width())))
#
#     imprecision = min(abs(imprecisionX), abs(imprecisionY))
#
#     print('imprecision in pixels X', imprecisionX)
#     print('imprecision in pixels Y', imprecisionY)
#     print('imprecision', imprecision)

# def set_to_size_old(grp, size, nb_of_repeats=26):
#     # even at 100 I get a small imprecision -−> maybe forget about that shit and take 26 always # dirty but ok for now -> I have bigger things to fix --> I tried 100 and it is perfect but 10 already seems to be enough --> maybe that is ok then --> even 3 is ok
#     # for some reason the stuff needs to be run several times to converge --> maybe some day I'll get the reason but it is ok and does not take time to do so!!!
#     for i in range(nb_of_repeats):
#         grp.set_to_size_old(size)
#         grp.size = size

def set_to_size(grp, size, nb_of_repeats=26):
    # even at 100 I get a small imprecision -−> maybe forget about that shit and take 26 always # dirty but ok for now -> I have bigger things to fix --> I tried 100 and it is perfect but 10 already seems to be enough --> maybe that is ok then --> even 3 is ok
    # for some reason the stuff needs to be run several times to converge --> maybe some day I'll get the reason but it is ok and does not take time to do so!!!
    for i in range(nb_of_repeats):
        grp.set_to_size(size)
        # grp.size = size


def set_to_width(grp, desired_width, nb_of_repeats=26):
    # in fact that was not so hard to do
    # Calculate the current aspect ratio of the object

    if grp.orientation != 'X':
        for i in range(nb_of_repeats):

            current_width = grp.getRect(all=True).width()
            current_height = grp.getRect(all=True).height()

            # print('falbala',current_width, current_height, desired_width)
            if current_width < 0 or current_height<0:
                # TODO --> KEEP DEV NOTE THIS PREVENTS INFINITE LOOPS WITH NEGATIVE VALUES
                #
                # current_width = grp.getRect().width()
                # current_height = grp.getRect().height()
                # print('falbala fixed', current_width, current_height, desired_width)
                current_width = 512
                current_height = 512

            aspect_ratio = current_height / current_width if current_width != 0 else 0

            factor_from_current_width_to_desired_width = desired_width/current_width
            desired_height = current_height * factor_from_current_width_to_desired_width

            # corresponding_desired_height = current_width * aspect_ratio

            # corresponding_desired_height = current_width*aspect_ratio
            # factor_from_current_width_to_predicted_height = corresponding_desired_height/

            grp.set_to_size(desired_height)
        grp.size = grp.width()

            # print('aspect_ratio CURRENT CHECK ', aspect_ratio, grp.getRect(), desired_width, desired_height)
    else:
        set_to_size(grp, desired_width, nb_of_repeats=nb_of_repeats)
        grp.size = grp.width()

def set_to_height(grp, desired_height, nb_of_repeats=26):
    if grp.orientation != 'Y':
        for i in range(nb_of_repeats):
            current_width = grp.getRect(all=True).width()
            current_height = grp.getRect(all=True).height()

            # print('falbala',current_width, current_height, desired_width)
            if current_width < 0 or current_height<0:
                # TODO --> KEEP DEV NOTE THIS PREVENTS INFINITE LOOPS WITH NEGATIVE VALUES
                #
                # current_width = grp.getRect().width()
                # current_height = grp.getRect().height()
                # print('falbala fixed', current_width, current_height, desired_width)
                current_width = 512
                current_height = 512

            aspect_ratio = current_width / current_height if current_height != 0 else 0

            factor_from_current_height_to_desired_height = desired_height / current_height
            desired_width = current_width * factor_from_current_height_to_desired_height

            grp.set_to_size(desired_width)
        grp.size = grp.height()

            # print('aspect_ratio CURRENT CHECK ', aspect_ratio, grp.getRect(), desired_width, desired_height)
    else:
        set_to_size(grp, desired_height, nb_of_repeats=nb_of_repeats)
        grp.size = grp.height()


    # Calculate the new height based on the desired width and the aspect ratio
    # new_height = desired_width * aspect_ratio
def set_to_width_im2d(rect, desired_width):
    current_width = rect.width()
    current_height = rect.height()
    aspect_ratio = current_height / current_width if current_width != 0 else 0

    factor_from_current_width_to_desired_width = desired_width / current_width
    desired_height = current_height * factor_from_current_width_to_desired_width

    # corresponding_desired_height = current_width * aspect_ratio

    rect.set_to_scale(current_width / desired_width)
    # corresponding_desired_height = current_width*aspect_ratio
    # factor_from_current_width_to_predicted_height = corresponding_desired_height/
    # grp.set_to_size(desired_height)
    # return new_rect

def set_to_height_im2d(rect, desired_height):
    # current_width = rect.width()
    # current_height = rect.height()
    # aspect_ratio = current_width / current_height if current_height != 0 else 0
    #
    # desired_width = current_width * (desired_height / current_height)
    # rect.set_to_scale(1./(desired_width/desired_height))

    current_width = rect.width()
    current_height =rect.height()
    aspect_ratio = current_width / current_height if current_height != 0 else 0

    factor_from_current_height_to_desired_height = desired_height / current_height
    desired_width = current_width * factor_from_current_height_to_desired_height

    # grp.set_to_size(desired_width)
    rect.set_to_scale(current_height/desired_height)

    # new_rect = QRectF(rect.x(), rect.y(), desired_width, desired_height)

    # return new_rect

# def set_to_width(grp, size, nb_of_repeats=26):
#     for i in range(nb_of_repeats):
#         grp.set_to_size(size)

def areIndicesOverlapping(indices_of_all_shapes):

    # Iterate over the indices_of_all_shapes list
    for i in range(len(indices_of_all_shapes) - 1):
        # Get the current and next elements
        curr = indices_of_all_shapes[i]
        next = indices_of_all_shapes[i + 1]

        # print('curr, next', curr, next)

        # Check if the elements overlap
        if curr[1] >= next[0]:
            # print('Overlap found between elements', i, 'and', i + 1)
            return True
    return False


class Group(Rectangle2D):
    _count=0 # this is a class variable

    # NB maybe is text could contain the text position instead of true such as above or below --> and it would adjust to stuff below it --> TODO
    def __init__(self, *args, space=3, x=None,y=None, width=None, height=None, fill_color=None, content=None, orientation=ORIENTATIONS[0], size=512, isText=False, add_empty_images_instead_of_None=True,**kwargs): # TODO DO NOT CALL IT ORIENTATION AS IT CAN BE MIXED WITH ANGLE -−> NEED SMARTER NAME
        # if kwargs:
        #     print('ignored parameters', kwargs)

        if x is not None and y is not None and width is not None and height is not None:
            super(Rectangle2D, self).__init__(x,y,width,height)
        else:
            super(Rectangle2D, self).__init__()

        # if self.width() == 0 and self.height==0:
        #     self.setWidth(size)
        #     self.setHeight(size)


        # in fact I need to reload content


        self.content = []
        self.space = space
        if isinstance(orientation, str):
            # legacy .pyf files serialize orientation with embedded quotes ('"X"')
            orientation = orientation.strip().strip('\'"') or ORIENTATIONS[0]
        self.orientation=orientation
        if args:
            for arg in args:
                if isinstance(arg, str):
                    arg = Image2D(arg) # TODO --> need make this smarter especially with custom code files
                if arg is None and add_empty_images_instead_of_None:
                    if self.content:
                        last = self.content[-1]
                        if isinstance(last, Image2D):
                            w,h = last.get_raw_size()
                            tmp = Image2D(width=w, height=h, crop_left=last.crop_left, crop_right=last.crop_right,crop_top=last.crop_top,crop_bottom=last.crop_bottom, theta=last.theta) # a true clone of the last
                            self.content.append(tmp)
                else:
                    if arg is not None:
                        self.content.append(arg)

        if isinstance(content, dict) or (isinstance(content, list) and content
                                         and all(isinstance(c, dict) for c in content)):
            # Reload content from serialized object (a list of one-key dicts
            # keeps the order of mixed groups and images)
            content = create_objects_from_dict(content)
            self.content.extend(content)

        # print(self.content)
        # if size is not None:
        self.size = size # maybe useful and I need to store that ??? -−> the good thing is that it will not change and so it is better
        # set_to_size(self,size) # shall I use that ??? --> maybe ...
        try:
            self.set_to_size(self.size) # very good but maybe I also need to update it
            set_to_width(self, self.size) # for now force size in x only to simplify things
        except (ArithmeticError, ValueError):
            # panels squeezed to nothing (too many gaps for the width, very
            # deep nesting): the layout divides by zero. The group used to be
            # dropped by the loader — most of a figure gone on open, and lost
            # on the next save. Keep it, with its content as saved.
            traceback.print_exc()
        Group._count += 1
        self.ID = Group._count
        self.fill_color = fill_color
        self.immutable = False
        self.isText = isText # this is just for pure text groups (will have a different behaviour on double click)
        # self.scale = 1

  # List-like behavior
    def __getitem__(self, key):
        # print(key)
        return self.content[key]

    def __len__(self):
        return len(self.content)

    def __iter__(self):
        return iter(self.content)

    def index(self, item):
        return self.content.index(item)
    # def __delitem__(self, index):
    #     del self[index]
    #
    def remove(self, *value):

        try:

            # print('stuff to be removed', value)

            # del self.content(value)
            # idx = self.content.index(value)
            # del self[idx]
            # self.content.remove(value)
            # self.content = [x for x in self.content if x not in value]
            for element in value:
                try:
                    self.content.remove(element)
                except Exception:
                    pass
                for inner in self.content:
                    try:
                        inner.remove(*value)
                        if inner.isEmpty():
                            self.content.remove(inner)
                    except Exception:
                        pass

            if not self.isEmpty():
                try:
                    # print('resizing', self, self.content)
                    set_to_size(self, self.width() if self.orientation == 'X' else self.height())
                except Exception:
                    # print('just for info for now, comment that lines in the future')
                    traceback.print_exc()
                    print('just for info for now, comment that lines in the future')
                    pass
                # i need go through all the stuff inside --> not that easy
            # shall I resize it ??? TODO --> PROBABLY YES BECAUSE SIMPLER

        except Exception:
            traceback.print_exc()
            pass

    def update(self):
        try:
            if not self.isEmpty():
                # print('updating', self, self.content)
                # set_to_size(self, self.width() if self.orientation == 'X' else self.height())
                set_to_size(self, self.size)
        except Exception:
            traceback.print_exc()
            print('just for info for now, comment that lines in the future')
            pass

    def isEmpty(self):
        return not self.content

    def pack(self):
        pack2(self.space, self.orientation,False, *self.content)

    def align(self):
        if self.orientation == 'X':
            align2(align_positions[0], *self.content) # align top
        else:
            align2(align_positions[2], *self.content)  # align Left

    def set_to_scale(self, scale):
        # the set to scale should change the size of the object --> either in width or in height depending on the object
        # TODO
        # maybe need repack if it is a group


        # print('I have been called', scale)

        # the scale of this one has to be magic and launch many more stuff

        if self.orientation == 'X':
            self.set_to_size(self.width() / scale)
        else:
            self.set_to_size(self.height()/scale)
        # self.scale = 1
        # pass

    # def set_to_size_neo(self, desired_size):
    #     all_ok=False
    #
    #     for elm in self:
    #         if elm.isText:
    #             all_ok=True
    #             break
    #
    #     # print('all_ok', all_ok)
    #
    #     if not all_ok:
    #         return self.set_to_size_old(desired_size)
    #
    #     if self.orientation == 'X':
    #         max_w = 0
    #         max_h = 0
    #         failed_images = []
    #         text_images = []
    #         individual_width = []
    #         individual_height = []
    #         for elm in self:
    #             # try:
    #                 if elm.isText:
    #                     individual_width.append(elm.annotations[0].width(all=True))
    #                     individual_height.append(elm.annotations[0].height(all=True))
    #                     max_w = max(elm.annotations[0].width(all=True), max_w)
    #                     max_h = max(elm.annotations[0].height(all=True), max_h)
    #                     text_images.append(elm)
    #                 else:
    #                     # pass # if fails this is not a text image
    #                     failed_images.append(elm)  # if image is failed then we have it
    #
    #         # I need to fit to the desired width
    #         desired_width = desired_size
    #         target_width_without_txt = desired_width - sum(individual_width)
    #
    #         # fit into a group with the desired stuff
    #
    #         print('max_w, max_h', max_w, max_h)
    #         print('individual_width', individual_width)
    #         print('individual_height', individual_height)
    #         print('desired_width', desired_width)
    #         print('target_width_without_txt',
    #               target_width_without_txt)  # it is probably a bit more complex because I need also the spacer and the nb of elems of the spacer inside and outside
    #         print('elems in', len(failed_images))
    #         print('elems out', len(self) - len(failed_images))
    #         # try to do the fit --> TODO
    #
    #         # TODO --> pack to the size
    #         # incompressible_space_of_group = (len(self.paint.EZFIG_panel.selected_shape)-1)*3
    #         incompressible_space_of_group = (len(text_images)) * self.space
    #         target_width_without_txt -= incompressible_space_of_group
    #
    #         # I need fit the stuff
    #
    #         # create a sub group for the failed images and set its size
    #         tmp = Group(*failed_images, space=self.space, orientation='X', size=target_width_without_txt)
    #         set_to_width(tmp, target_width_without_txt)
    #
    #         # then get the height of the group
    #
    #         max_h = tmp.height()
    #         # put the other images back into their stuff and just launch the packing of the group
    #         # and resize the images to that size
    #
    #         for iii, elm in enumerate(text_images):
    #             # elm.scale=1.
    #             elm.setHeight(max_h)
    #             elm.setWidth(individual_width[iii])
    #             elm.set_to_scale(1)
    #
    #         self.pack()
    #         self.align()
    #         self.update_bounds()
    #         # self.update()
    #     else:
    #
    #
    #         print('entering orientation Y', self)
    #         # this works but the embeded does not --> why is that
    #
    #         # i need to fit all the shapes without the stuff to the desired width then just readd the other stuff
    #
    #         # I need get the height
    #
    #         # ça marche --> ça donne un moyen facile de faire tout ce que je voulais
    #         # now we fix the code so that we fit the height of an object according to that of the others --> TODO
    #         max_w = 0
    #         max_h = 0
    #         failed_images = []
    #         text_images = []
    #         individual_width = []
    #         individual_height = []
    #         for elm in self:
    #             if elm.isText:
    #                 individual_width.append(elm.annotations[0].width(all=True))
    #                 individual_height.append(elm.annotations[0].height(all=True))
    #                 max_w = max(elm.annotations[0].width(all=True), max_w)
    #                 max_h = max(elm.annotations[0].height(all=True), max_h)
    #                 text_images.append(elm)
    #             else:
    #                 # pass # if fails this is not a text image
    #                 failed_images.append(elm)  # if image is failed then we have it
    #
    #         # I need to fit to the desired width
    #         desired_width = desired_size  # 256 #
    #         target_width_without_txt = desired_width  # since it is a col it does not need all of that
    #
    #         # fit into a group with the desired stuff
    #
    #         print('max_w, max_h', max_w, max_h)
    #         print('individual_width', individual_width)
    #         print('individual_height', individual_height)
    #         print('desired_width', desired_width)
    #         print('target_width_without_txt',
    #               target_width_without_txt)  # it is probably a bit more complex because I need also the spacer and the nb of elems of the spacer inside and outside
    #         print('elems in', len(failed_images))
    #         print('elems out', len(self) - len(failed_images))
    #         # try to do the fit --> TODO
    #
    #         # TODO --> pack to the size
    #         # incompressible_space_of_group = (len(self.paint.EZFIG_panel.selected_shape)-1)*3
    #         incompressible_space_of_group = (len(text_images)) * 3
    #         # target_width_without_txt -= incompressible_space_of_group
    #
    #         # I need fit the stuff
    #
    #         # create a sub group for the failed images and set its size
    #         tmp = Group(*failed_images, space=3, orientation='X')
    #         set_to_width(tmp, target_width_without_txt)
    #
    #         # then get the height of the group
    #
    #         max_w = tmp.width()
    #         # put the other images back into their stuff and just launch the packing of the group
    #         # and resize the images to that size
    #
    #         for iii, elm in enumerate(text_images):
    #             # elm.scale=1.
    #             elm.setHeight(individual_height[iii])
    #             elm.setWidth(max_w)
    #             elm.set_to_scale(1)
    #
    #
    #
    #         # del tmp
    #         # just pack the shape and nothing else and set x to 0
    #         # align top and pack
    #         # self.paint.EZFIG_panel.selected_shape.pack()
    #         # self.paint.EZFIG_panel.selected_shape.align()
    #         # self.paint.EZFIG_panel.selected_shape.update_bounds()
    #
    #         set_to_width(self, target_width_without_txt)
    #
    #         print('inner update', self.update_bounds())

    def set_to_size(self, desired_size):
        sum_along_axis = self.get_incompressible_size(axis=self.orientation)
        if self.orientation == 'X':
            resize_rects_within_total_width(self.content, desired_size, sum_along_axis)
            # resize_rects_within_total_width(self.content, desired_size, self.space)
        else:
            # resize_rects_within_total_height(self.content, desired_size, self.space)
            resize_rects_within_total_height(self.content, desired_size, sum_along_axis)


        # if True:
        #     print('beforesdsqdq0')
        #     self.check_coords()

        self.pack()
        # if True:
        #     print('beforesdsqdq1')
        #     self.check_coords()

        self.align()
        # if True:
        #     print('beforesdsqdq2')
        #     self.check_coords()
        self.update_bounds()

    # def set_to_size_old(self, desired_size):
    #     # for i in range(100): # weird but somehow I need a convergence and iteration stuff (is that due to a bug, can I iterate in a smarter manner) ???
    #     #     print('entering the real shit')
    #         sum_along_axis = self.get_incompressible_size(axis=self.orientation)
    #         if self.orientation == 'X':
    #             resize_rects_within_total_width(self.content, desired_size, sum_along_axis)
    #             # resize_rects_within_total_width(self.content, desired_size, self.space)
    #         else:
    #             # resize_rects_within_total_height(self.content, desired_size, self.space)
    #             resize_rects_within_total_height(self.content, desired_size, sum_along_axis)
    #
    #         # if True:
    #         #     print('beforesdsqdq0')
    #         #     self.check_coords()
    #
    #         self.pack()
    #         # if True:
    #         #     print('beforesdsqdq1')
    #         #     self.check_coords()
    #
    #         self.align()
    #         # if True:
    #         #     print('beforesdsqdq2')
    #         #     self.check_coords()
    #         self.update_bounds()

    def check_coords(self):
        for iii,img in enumerate(self):
            print('iii', iii, '-->', img.getRect())

    def checkAR(self):
        for iii, rect in enumerate(self.content):
            print(are_ratios_almost_equal(rect.width() / rect.height(), rect.width(all=True) / rect.height(all=True)), 'old AR', rect.width() / rect.height(), 'new AR', rect.width(all=True) / rect.height(all=True))

    # NB THE RECT AND WIDTH OF GROUP SHOULD NOT BE SCALABLE !!! --> see how I can do this in a cleaner way !!!!
    def getRect(self,*args, **kwargs):
        # if args or kwargs:
            return QRectF(self.x(), self.y(), self.width(), self.height())
        # else:
        #     # return super().getRect()
        #     return QRectF(*super().getRect())
    def width(self,*args, **kwargs):
            # return self.width()
        # else:
            return super().width()

    def height(self,*args, **kwargs):
        # if args or kwargs:
        #     return self.height()
        # else:
            return super().height()

    def update_bounds(self):
        # Initialize bounding_rect with maximum and minimum values
        bounding_rect = [float('inf'), float('inf'), float('-inf'), float('-inf')]

        for rect in self.content:
            bounding_rect[0] = min(bounding_rect[0], rect.x())
            bounding_rect[1] = min(bounding_rect[1], rect.y())
            bounding_rect[2] = max(bounding_rect[2], rect.x() + rect.width(all=True))
            bounding_rect[3] = max(bounding_rect[3], rect.y() + rect.height(all=True))

        self.setRect(bounding_rect[0], bounding_rect[1], bounding_rect[2] - bounding_rect[0],
                     bounding_rect[3] - bounding_rect[1])
        # print('bounding rect', self.getRect(scale=True))




    def getCombinedBoundsAtIndices(self, image_indices):
        if not image_indices:
            return None
        # if isinstance(image_indices, int):
        #     in
        # for each there will be a begin and an end
        begin, end = image_indices
        # if begin == end:
        #     print('same begin and end')

        # print('begin, end', begin, end)



        # how can I keep assocition despite serialization --> by storing the element into another --> but that would complicate a bit the things though -−> see how I can do that
        # or just say if it should be associated to above or below ????
        if begin>end: # begin should always be before end
            begin, end = end, begin

        if begin<0:
            begin = 0
        if end>=len(self.content):
            end = len(self.content)-1
        if end<0:
            end=0

        if begin>=0 and begin<len(self.content):
            begin_rect = self.content[begin].getRect(all=True)
            # print('begin_rect',begin_rect)
        if begin==end:
            return begin_rect
        if end>=0 and end < len(self.content):
            end_rect = self.content[end].getRect(all=True)
            # print('end_rect',end_rect)

        try:
            return begin_rect.united(end_rect) # this returns the combined rect of begin and end coordinates -−> that is exactly what I want
        except Exception:
            return None



    # untested
    def translate(self, *args):
        if len(args) == 1:
            point = args[0]
            QRectF.translate(self, point.x(), point.y())
            for img in self:
                img.translate(point.x(), point.y())
        else:
            QRectF.translate(self, args[0], args[1])
            for img in self:
                img.translate(QPointF(args[0], args[1]))

    # def swap(self, element1, element2): # so in fact it is not a swap it is a replace
        # find element1 and replace it with element2
        # swap can be seen as a chain of replace with inverting one by the other

    # def replace(self, element1, element2):
    #     pass

    # def swap(self, element1, element2):
        # loop
        # if not isinstance(__args[0], QPointF):
        #     for elm in self.content:
        #         if elm == __args[0]:
        #             return True
        #         if elm.contains(__args[0]):
        #             return True
        # else:
        #     if super().contains(
        #             *__args):  # if anything in there contains the point return the containing element else return False
        #         for elm in self.content:
        #             if elm.contains(*__args):
        #                 return elm
        #         return True
        # return False

    def move_left(self, elements, distance=1):
        if elements is None:
            return
        if distance <=0:
            return
        if not isinstance(elements, list):
            elements = [elements]

        list_of_iterables = get_iterable_elements(self)
        for elm in list_of_iterables:
            indices = [i for i, x in enumerate(elm.content) if x in elements]
            elm.content = move_left(elm.content, indices, distance) # get indices


        # TODO --> do it recursive inside -−> TODO


    def move_right(self, elements, distance=1):
        if elements is None:
            return
        if distance <=0:
            return
        if not isinstance(elements, list):
            elements = [elements]
        # indices = [i for i, x in enumerate(self.content) if x in elements]
        # self.content = move_right(self.content, indices, distance) # get indices
        list_of_iterables = get_iterable_elements(self)
        for elm in list_of_iterables:
            indices = [i for i, x in enumerate(elm.content) if x in elements]
            elm.content = move_right(elm.content, indices, distance)  # get indices

    def draw_inner_layout_selection(self, painter):
        painter.save()
        try:
            inner_elements = get_all_contained_images(self)
            # painter.setPen(QPen(QColor(0, 255, 255)))

            for elm in inner_elements:
                # rect = elm.getRect(scale=True)
                # painter.drawRect(rect)
                elm.draw_inner_layout_selection(painter)
        except Exception:
            print('inner error')
            traceback.print_exc()
        painter.restore()


    def draw(self, painter, draw=True):

        if draw:
            painter.save()
            rect_to_plot = self.getRect()
            if self.fill_color is not None:
                # if the user wants to really draw a bg with a given color between the images -−> then I draw this first before drawing anything else
                painter.setBrush(QBrush(QColor(self.fill_color)))
                painter.drawRect(rect_to_plot)

            for img in self:
                img.draw(painter, draw=draw)

            painter.restore()

            # debug
            if False:
                pen = QPen(QColor(0xFF00FF))
                pen.setWidthF(3)
                painter.setPen(pen)

                # print('rect_to_plot',rect_to_plot)

                painter.drawRect(rect_to_plot)

    # as much as it is possible do get rid of fill to better organize the stuff
    # def fill(self, painter, draw=True):
    #     if self.fill_color is None:
    #         return
    #     if draw:
    #         painter.save()
    #         for img in self:
    #             img.fill(painter, draw=draw)
    #         painter.restore()
    #
    # def drawAndFill(self, painter):
    #     painter.save()
    #     self.draw(painter, draw=True)
    #     painter.restore()

    def get_incompressible_size(self, axis=None):
        # return the meaningful incompressible state of the image
        # pass
        # if self.orientation == 'X':
        # print('group_count', self._count)
        if axis is None:
            # print('sum_incompressible_along_axis2', self.space*(len(self.content)-1))
            return self.space*(len(self.content)-1) # THAT IS NOT ENOUGH I ALSO NEED ALL THE PROGENY INCOMPRESSIBLE SPACE IN THIS ORIENTATION --> TODO
        else:
            sum_incompressible_along_axis = 0

            # If I don't put the below line then the size works --> I am overestimating the stuff !!!
            # for elm in self.content:
            #     sum_incompressible_along_axis+=elm.get_incompressible_size(axis=axis)
            # for elm in self.content:
            #     sum_incompressible_along_axis+=elm.get_incompressible_size(axis=axis) # in fact I should not atke into account the others
            if self.orientation == axis:
                sum_incompressible_along_axis+=self.space*(len(self.content)-1)
            # print('sum_incompressible_along_axis', axis, sum_incompressible_along_axis, len(self.content), self.space, self.orientation, self._count)
            return sum_incompressible_along_axis

    def setTopLeft(self, *args):
        if args:
            cur_top_left = self.topLeft()
            # print('cur_top_left', cur_top_left, args)
            if len(args)==1:
            #     # assume a QpointF
                for img in self.content:
                    # img.moveTopLeft(args[0])
                    img.translate(args[0].x()-cur_top_left.x(), args[0].y()-cur_top_left.y())
            elif len(args) == 2:
                for img in self.content:
                    img.translate(args[0] - cur_top_left.x(), args[1] - cur_top_left.y())
            self.update_bounds()
            # elif len(args)==2:
            #     for img in self.content:
            #         img.moveTopLeft(QPointF(args[0], args[1]))
            # else:
            #     # logger.error('invalid args for top left')
            #     print('invalid args for top left')

    def replace(self, old, new): # NB THIS IS NOT RECURSIVE SO IT SHOULD BE USED ONLY WITH THE IMMEDIATE PARENT
        if old in self.content:
            self.content[self.content.index(old)]=new

    def __contains__(self, item):
        return item in self.content

    def __setitem__(self, index, item):
        self.content[index] = item

    def get_nested_groups(self):
        groups = [self]
        if self.content:
            for group in self.content:
                if isinstance(group, Group):
                    groups.extend(group.get_nested_groups())
        return groups

    def contains(self, *__args):
        # hacked contains that checks whether a point or an image is contained in the stuff
        # see for images

        # if not __args:
        #     return False
        # if len(__args)==2:
        #     # check if an innner object contains a point and return it
        #     for elm in self.content:
        #         if elm.contains()
        # else:
        #     if isinstance(__args[0],Rectangle2D):
        #         if self == __args[0]:
        #             return True
        #     else:
        #         return super().getRect(scale=True).contains(*__args)

        if not isinstance(__args[0], QPointF):
            for elm in self.content:
                if elm == __args[0]:
                    # print('elm found by equal', elm, __args[0])
                    return True
                try:
                    if __args[0] in elm: # I had to override contains in images to avoid issues
                        # print('elm found by other way', __args[0], elm, __args[0] in elm)
                        return True
                except Exception:
                    pass # if not iterable then anyway cannot contain the stuff
        else:
            if super().contains(*__args): # if anything in there contains the point return the containing element else return False
                for elm in self.content:
                    if elm.contains(*__args):
                        return elm
                return True
        return False

    def extend(self, lst):
        try:
            self.content.extend(lst)
        except Exception:
            # self.content.add(lst) # in case it is not a list then just add is
            self.add(lst)

    def add(self, item):
        self.content.append(item)

    # be careful with that because this is what is compared when using == !!! so if poorly implemented this can have dramatic effects
    def __str__(self):
        # return f"group {self.ID}"
        return self.__repr__()

    def __repr__(self): # required to appear in the printed list
        # return self.__str__()
        class_name = type(self).__name__
        memory_address = hex(id(self))
        return f"{class_name}-{self.ID}-{memory_address}"



# probably the AR of the group should take into account the incompressible stuff --> this is why it is unfixed untill
# there is always a solution for 0 space --> how can I from the 0 space find all the other solutions???
if __name__ == '__main__':
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
    img10b = Image2D('/E/Sample_images/counter/10.png')
    if True:
        grp1 = Group(Group(img0, img1, img2, img3), img4, Group(img5, Group(img6, img7, img8)), img9)
        print(get_all_contained_images(grp1))
        # print(get_iterable_elements(grp1))
        sys.exit(0)

        print('parent_of_obj',get_parent_of_obj(img9, grp1))
        print('parent_of_obj',get_parent_of_obj(img4, grp1))
        print('parent_of_obj',get_parent_of_obj(img0, grp1)) # there is a bug
        print('parent_of_obj',get_parent_of_obj(img1, grp1))
        print('parent_of_obj',get_parent_of_obj(img5, grp1))
        print('parent_of_obj',get_parent_of_obj(img6, grp1))
        print('parent_of_obj',get_parent_of_obj(img7, grp1))
        print('parent_of_obj',get_parent_of_obj(img8, grp1))

        sys.exit(0)



        grp1 = Group(Group(img0,img1, img2, img3), img4, Group(img5, Group(img6, img7, img8)), img9)
        # print('all_iterables',get_iterable_elements(grp1))
        print(grp1.content)
        print(grp1.content[0].content)
        print(grp1.content[2].content)
        print(grp1.content[2].content[1].content)
        grp1.move_left([img1, img8, img9])  # really need to pass a list
        print('out')
        print(grp1.content)
        print(grp1.content[0].content)
        print(grp1.content[-1].content)
        print(grp1.content[-1].content[1].content)
        # print(grp1.content[2].content[1].content)
        # print(grp1.content[2].content)
        # print('bob')
        grp1 = Group(img0,img1, img2, img3, img4,img5, img6, img7, img8, img9)
        # print('all_iterables2', get_iterable_elements(grp1))





        # sys.exit(0)
        print('old')
        grp1 = Group(img0, img1, img2, img3, img4, img5, img6, img7, img8, img9)
        print(grp1.content)
        grp1.move_left(img1) # really need to pass a list
        print(grp1.content)
        print('bob')


        grp1 = Group(img0, img1, img2, img3, img4, img5, img6, img7, img8, img9)
        print(grp1.content)
        grp1.move_left([img0, img1, img6])
        print(grp1.content)

        grp1 = Group(img0, img1, img2, img3, img4, img5, img6, img7, img8, img9)
        print(grp1.content)
        grp1.move_right([img0, img1, img6])
        print(grp1.content)

        print('with errors and missing')
        grp1 = Group(img0, img2, img3, img4, img5, img6, img7, img8, img9)
        print(grp1.content)
        grp1.move_left([img2, img1, img6])
        print(grp1.content)

        grp1 = Group(img0, img2, img3, img4, img5, img6, img7, img8, img9)
        print(grp1.content)
        grp1.move_right([img0, img1, img6])
        print(grp1.content)
        grp1.move_right([img0, img1, img6])
        print(grp1.content)
        for i in range(10):
            grp1.move_right([img0, img1, img6])
        print(grp1.content)
        sys.exit(0)

    if True:



        grp1 = Group(img0, img1)
        print(isinstance(grp1, list))
        print(isinstance(grp1, Group)) # very good
        grp2 = Group(img2, img3)
        grp1.extend(grp2)
        print(grp1.content)
        grp1.extend(img10b)
        print(grp1.content)




        grp3 = Group(img4, img5)
        grp4 = Group(img6, img7)
        grp3.add(grp4)
        print(grp3.content)

        grp5 = Group(img8, img9, img10)
        grp5.remove(img10)
        print(grp5.content)

        grp5.add(Group(img10))
        print(grp5.content)
        grp5.remove(img10) # very good --> the parent group is empty
        print(grp5.content)


        # for extend --> maybe autodelete stuff














        sys.exit(0)

    app = QApplication(sys.argv)  # IMPORTANT KEEP !!!!!!!!!!! # required to use strings
    html = '''
    <!DOCTYPE html>
    <html>
      <head>
        <title>Font Face</title>
      </head>
      <body>
        <font color="red">
          <font face="Symbol" size="5">Symbol</font><br />
          <font face="Times New Roman" size="5">Times New Roman</font><br />
          <font face="Verdana" size="5">Verdana</font><br />
          <font face="Comic Sans MS" size="5">Comic Sans MS</font><br />
          <font face="WildWest" size="5">WildWest</font><br />
          <font face="Bedrock" size="5">Bedrock</font><br />
        </font>
      </body>
    </html>
    '''

    html = '''
    <!DOCTYPE html>
    <html>
      <head>
        <title>Font Face</title>
      </head>
      <body>
        <font color="red">
          <font face="Symbol" size="5">Symbol</font><br />
          <font face="Times New Roman" size="5">Times New Roman</font><br />
          <font face="Bedrock" size="5">Bedrock</font><br />
        </font>
      </body>
    </html>
    '''

    # this works super well -−> I can think of finalizing it very soon !!!

    # VERY GOOD -−> TRY TO FIX ALL THE STUFF!!!

    if True:
        # img1 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        # img2 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        # img3 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        # img4 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))

        # img1 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        # img2 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        # img3 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        # img4 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        img1 = Image2D('/E/Sample_images/counter/00.png')
        img2 = Image2D('/E/Sample_images/counter/01.png')
        img3 = Image2D('/E/Sample_images/counter/02.png')
        img4 = Image2D('/E/Sample_images/counter/03.png')
        img5 = Image2D('/E/Sample_images/counter/05.png')
        img6 = Image2D('/E/Sample_images/counter/06.png')
        img7 = Image2D('/E/Sample_images/counter/07.png')
        img8 = Image2D('/E/Sample_images/counter/08.png')
        img9 = Image2D('/E/Sample_images/counter/09.png')

        grp1 = Group(img1, img2)
        grp5 = Group(img5, img6, Group(img7, img8, orientation='Y'))
        grp2 = Group(img3, img4,grp5, orientation='Y')



        grp3 = Group(grp1, grp2)


        set_to_size(grp3,512)

        point = random.choice([QPointF(64,64),QPointF(430,100)])
        print(point)
        elements_under_selection = []
        elm = grp3
        while elm:
            if isinstance(elm, bool):
                break
            elements_under_selection.append(elm)
            elm = elm.contains(point)
        print(elements_under_selection)


        # this is the code to get all the elements below the stuff

        # for elm in elements_under_selection:
        #     print(type(elm))
        #
        # elm = grp3.contains(QPointF(64,64))
        # if elm:
        #     print('contained',elm)
        #     print(elm == img1)
        #     print(elm == img2)
        #     print(elm==grp1)
        #     print(elm == grp2)
        #     print(elm == grp3)
        # else:
        #     print('not contained')
        #
        # elm = grp3.contains(QPointF(430,32))
        # if elm:
        #     print('contained', elm)
        #     print(elm == img1)
        #     print(elm == img2)
        #     print(elm == grp1)
        #     print(elm == grp2)
        #     print(elm == grp3)
        # else:
        #     print('not contained')

        # print(group._count)
        # print(grp3, grp2)

        print('grp3.contains(img1)', grp3.contains(img1))
        print('grp3.contains(img1)', grp3.contains(img4))
        print('grp3.contains(img1)', grp3.contains(img8))
        print('#'*20)
        print('grp3.contains(img1)', grp1.contains(img1))
        print('grp3.contains(img1)', grp1.contains(img4))
        print('grp3.contains(img1)', grp2.contains(img1))
        print('grp3.contains(img1)', grp2.contains(img4))
        print('grp3.contains(img1)', grp2.contains(img8))

        preview(grp3)

        sys.exit(0)

    if False:
        '''
        solution of a grp that has two images in a row and 2 images in a col
        PyQt6.QtCore.QRectF(0.0, 0.0, 511.99999999999994, 202.99999999999997)
        
        ###sub###
        PyQt6.QtCore.QRectF(0.0, 0.0, 408.99999999999994, 202.99999999999997)
        -−>  PyQt6.QtCore.QRectF(0.0, 0.0, 202.99999999999997, 202.99999999999997)
        -−>  PyQt6.QtCore.QRectF(205.99999999999997, 0.0, 202.99999999999997, 202.99999999999997)
        PyQt6.QtCore.QRectF(411.99999999999994, 0.0, 100.0, 202.99999999999997)
        -−>  PyQt6.QtCore.QRectF(411.99999999999994, 0.0, 99.99999999999999, 99.99999999999999)
        -−>  PyQt6.QtCore.QRectF(411.99999999999994, 102.99999999999999, 99.99999999999999, 99.99999999999999)
        
        so each small rect in col should be 100*100 and each big rect should be 203*203
        
        -> now figure the math for that
        
        if I put all same size (no space) can I compute the rect and then adjust space so that it still fits ??? --> not so easy
        
        total_uncompressible_width = 512-(3-1)*3 = 506
        target_height = 512/512+512/512+256/512 = 2.5 --> 202.4 --> I almost have it real AR for last is in fact 256/(512-3)
        
        the real AR factor should be 2.492611 to get 202.9999999 of height for both col group and for --> how can I get there ????
        # there isn't probably any solution and I need iter but with a good initial guess 
        # --> take AR by default and adjust
        
        solution for two groups of 256x512 and 512x512  -−> 138.54
        PyQt6.QtCore.QRectF(0.0, 0.0, 512.0, 138.54545454545453)
        ###sub###
        PyQt6.QtCore.QRectF(0.0, 0.0, 418.6363636363636, 138.54545454545453)
        -−>  PyQt6.QtCore.QRectF(0.0, 0.0, 277.09090909090907, 138.54545454545453)
        -−>  PyQt6.QtCore.QRectF(280.09090909090907, 0.0, 138.54545454545453, 138.54545454545453)
        PyQt6.QtCore.QRectF(421.6363636363636, 0.0, 90.36363636363637, 138.54545454545453)
        -−>  PyQt6.QtCore.QRectF(421.6363636363636, 0.0, 90.36363636363636, 45.18181818181818)
        -−>  PyQt6.QtCore.QRectF(421.6363636363636, 48.18181818181818, 90.36363636363636, 90.36363636363636)
        
        total_uncompressible_width = 512-(3-1)*3 = 506
        target_height = 512/256+512/512+ 90.363636/138.54545454545454 --> 3.652231 -−> perfect --> that is this one --> I need do it like that --> not that hard in fact 
        
        # je dois trouver 3.6 --> ça ne marche pas du tout -> réflechir en fait
        
        # how can I handle the incompressible texts--> see that later
         
        '''
        img1 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img2 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img3 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img4 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))

        img1 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        img2 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        img3 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        img4 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))

        grp1 = group(img1,img2)
        grp2 = group(img3, img4, orientation='Y')

        grp3 = group(grp1, grp2)
        # grp3.set_to_size(512)
        set_to_size(grp3,512)

        print(grp3.getRect())

        print(grp3.get_incompressible_size(axis=grp3.orientation)) # --> 6 --> ok

        get_imprecision(grp3,512) # --> imprecision of 3 pixels


        print('###sub###')

        for elm in grp3:
            print(elm.getRect(scale=True))
            for el in elm:
                print('-−> ', el.getRect(scale=True))

        preview(grp3)


        sys.exit(0)

    if True:
        # that works

        img1 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img2 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img3 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))
        img4 = Image2D(Img(np.zeros((512,512)), dimensions='hw'))

        img1 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        img2 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))
        img3 = Image2D(Img(np.zeros((256, 512)), dimensions='hw'))
        img4 = Image2D(Img(np.zeros((512, 512)), dimensions='hw'))

        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        fig, ax = plt.subplots()
        ax.plot(t, s)

        ax.set(xlabel='time (s)', ylabel='voltage (mV)', title=None)
        ax.grid()

        # plt.show()
        # fig.savefig("test.png")
        # plt.show()
        # ça marche --> voici deux examples de shapes
        fig = VectorGraphics2D(fig, x=0, y=0, width=20., height=10.)  # could also be used to create empty image with

        svg = VectorGraphics2D('/E/Sample_images/EZF_SF_scientifig_EZFig/sample_images_svg/cartman.svg', x=12, y=0,
                                 width=1, height=1, fill_color=0xFFFFFF) # pb is I can change size if I don't put

        # grp1 = group(img1,img2)
        # grp2 = group(img3, img4, orientation='Y')
        #
        # grp3 = group(grp1, grp2)


        # grp3 = group(img3, fig, space=42, orientation=random.choice(['X','Y']), fill_color=0xFF00FF)
        # grp3 = group(img3,fig, img1,svg, space=3, orientation=random.choice(['X','Y']), fill_color=0xFF00FF)
        grp3 = group(img3,fig, img1, space=3, orientation=random.choice(['X','Y']), fill_color=0xFF00FF)

        # grp3.set_to_size(512)
        set_to_size(grp3,1024)

        print(grp3.getRect())

        print(grp3.get_incompressible_size(axis=grp3.orientation)) # --> 6 --> ok

        get_imprecision(grp3,512) # --> imprecision of 3 pixels

        print('###sub###')

        for elm in grp3:
            print(elm.getRect(all=True))
            try:
                for el in elm:
                    print('-−> ', el.getRect(all=True))
            except Exception:
                pass



        preview(grp3)

        sys.exit(0)

    if False:

        # this now works I shouldn't take the text as immutable -−> I may need to resize the image every time text is added -−> need to think how I can do that
        # this is now broken because of immutable -> see how I can fix that

        img1 = Image2D('/E/Sample_images/counter/01.png')
        img2 = Image2D('/E/Sample_images/counter/01.png')
        img3 = Image2D('/E/Sample_images/counter/02.png')
        text = TAText2D(html)
        # text.set_rotation(-45)
        text.color = 0xFF0000

        # bug in set_to_scale of the stuff

        grp = group(text,img3,img1, fill_color=0xFFFFFF, orientation=random.choice(['X','Y'])) # --> correct
        # grp = group(text, img3, img1, fill_color=0xFFFFFF, orientation='Y') # --> this is incorrect in height --> see how I can handle that

        # I need a smarter code --> maybe only compute size of mutable  and scale them to size

        # for some reason I cannot always see the text --> what is this bug ???
        # debug it with just that

        # I need get the exact size of the text --> because now it seems much bigger than it really is

        # I also need to be able  to change the pen color of text --> I need split text by colors

        # shall I draw only the stuff within the rect ??? --> maybe

        # set_to_size(grp,512)
        grp.set_to_size(512) # --> good this is ok in X but then why not in Y???

        print(grp.getRect()) # not at all right size --> 307 --> not ok

        get_imprecision(grp)

        preview(grp)

        sys.exit(0)


    if False:

        # seems ok but see how to handle text ??? --> very hard because unscalable -−> or assume scalable and truncate the text
        # best is to treat it as an image with a fixed width and height

        # I need to treat the text independently of the rest of the figure and to crop it to the height of the others when done


        #sufficient to reproduce the size bug

        # mathematically it is unsolvable if uncompressible size is > to desired final size -−> I need a warning for the user !!! -−> TODO


        SPACE=10
        # SPACE=0

        img1 = Image2D('/E/Sample_images/counter/00.png')
        img2 = Image2D('/E/Sample_images/counter/01.png')
        img3 = Image2D('/E/Sample_images/counter/02.png')
        img4 = Image2D('/E/Sample_images/counter/03.png')
        img5 = Image2D('/E/Sample_images/counter/05.png')
        img6 = Image2D('/E/Sample_images/counter/06.png')
        img7 = Image2D('/E/Sample_images/counter/07.png')
        img8 = Image2D('/E/Sample_images/counter/08.png')
        img9 = Image2D('/E/Sample_images/counter/09.png')

        # I NEED MAKE SURE THAT THE SPACE IS NOT CRAEY OTHERWISE THAT CANNOT work
        grp1= group(img1,img2, img3, img4, img5, space=6)
        grp2= group(img6,img7, img8, img9, orientation='Y', space=3)
        grp3 = group(grp1, grp2, space=9, orientation=random.choice(['X','Y'])) # there is a big bug there

        # also sufficient to reproduce the bug...
        # grp1 = group(img1,img2, space=200) # this is the space missing --> why this bug??? " --> YES THIS IS ALWAYS THE SPACE MISSING --> WHY IS THAT!!!
        # grp2 = group(img6, orientation='Y', space=SPACE*20)
        # grp3 = group(grp1, grp2, space=SPACE*2)

        # indeed smthg needs be done recursively to match the size properly --> am I not getting the right size in some cases ????
        start = timer()

        # doing it 100 time fixes the size difference but there is still smthg missing --> so there is some convergence issue somewhere
        # for i in range(26):  # 5 to 10 times seems to be enough --> I can maybe live with that!!! # time is negligibly longer --> so I can afford to have that (it become a little bit longer if I go around 1000 there the error is null
        #     grp3.set_to_size(512)  # NB THE SET TO SIZE FIXED the BUG --> WHY DO I NEED TO DO IT TWICE
        set_to_size(grp3, 512)

        print('total time', timer()-start)

        # grp3.set_to_size(1024)  # NB THE SET TO SIZE FIXED the BUG --> WHY DO I NEED TO DO IT TWICE
        # grp3.set_to_size(1024)  # NB THE SET TO SIZE FIXED the BUG --> WHY DO I NEED TO DO IT TWICE

        print(grp3.orientation)
        print(grp3.space)
        print(grp3.get_incompressible_size())
        print(grp3.get_incompressible_size(axis=grp3.orientation))

        print(grp3.getRect()) # not ok --> probably need do this properly #(0.0, 0.0, 502.0, 218.7883919228763) vs (0.0, 0.0, 501.9999999999999, 216.95561080400537) when repeated once --> why not deterministic ???

        # why not all same height --> they should have the same

        # print(len(grp3))

        # if I take the unpacked size and append to it the incompressible size I should get back to the right shape

        print('####sub####')
        for elm in grp3:
            print(elm.getRect())

        print(grp1.space)
        print(grp1.orientation)


        # imprecisionX = grp3[0].getRect().height()-grp3[1].getRect().height()
        # imprecisionY =  grp3[0].getRect().width()-grp3[1].getRect().width()
        # imprecision = min(abs(imprecisionX), abs(imprecisionY))
        # print('imprecision in pixels X', imprecisionX)
        # print('imprecision in pixels Y', imprecisionY)
        # print('imprecision', imprecision)
        get_imprecision(grp3)

        #-4.663263553084107e-09 for 16 repeats
        # imprecision in pixels 0.0 for 100 or 50 or 30 or 26 repeats
        # imprecision in pixels 8.526512829121202e-14 for 25 repeats
        # -1.4921397450962104e-11 for 20 repeats
        # --> 26 is the first where I really get 0 --> ok


        preview(grp3)
        sys.exit(0)

    # Example usage:
    # custom_list = col(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    # print(custom_list[0])

    orientation='X' # all same height --> ok
    # orientation='Y' # pb --> not all same width but all same height --> NOT GOOD --> packing is ok and align also --> it is the scaling that sucks
    # almost ok but height is incorrect -−> not the target height --> need a fix
    # VERY GOOD --> NOW BOTH ARE FIXED -> TRY TO FINISH THAT VERY SOON -−> SHOULD BE DOABLE

    # ça marche ce truc behaves as a rect and as a list --> very useful in a way for iter
    if False:
        grp = group(Rectangle2D(QRectF(0, 0, 100, 50)),
            Rectangle2D(QRectF(20, 20, 200, 100)),
            Rectangle2D(QRectF(30, 30, 300, 150)),
            Rectangle2D(QRectF(60, 30, 200, 120)),
            Rectangle2D(QRectF(30, 30, 300, 100)), orientation=orientation)
    else:

        # --> all is ok and the size is an iteration issue -−> maybe then I should not worry about that

        INCOMPRESSIBLE_SPACE_TEST =10 # --> setting it to 0 fixes the misalignment --> that means that this is the incompressible part of the stuff that matters -> I need make functions that return the amount of incompressible space so that the AR CAN BE PROPERLY COMPUTED

        # grp = group(Image2D('/E/Sample_images/counter/00.png'), Image2D('/E/Sample_images/counter/01.png'),Image2D('/E/Sample_images/counter/02.png'),Image2D('/E/Sample_images/counter/03.png'))
        img1 = Image2D('/E/Sample_images/counter/00.png')
        img2 = Image2D('/E/Sample_images/counter/01.png')
        img3 = Image2D('/E/Sample_images/counter/02.png')
        img4 = Image2D('/E/Sample_images/counter/03.png')


        # it seems I had never reimplemented the rotation --> is that possible !!!
        img1.set_rotation(45)
        img3.set_rotation(-33)
        # img1 = Rectangle2D(QRectF(20, 20, 200, 100))
        # img1.set_rotation(45) # --> rotation roughly works for rectangle even though the bounds are not correct and the crop is not correct either!!!
        # but rotation

        # if rotated by 90degrees I would need to change the dimensions of the image and see also how to handle the other rotations ??? --> NEED THINK -−> IF NOT SAME SIZE -−> NEED BE SMART !!! --> TODO

        img4.set_rotation(90) # TODO --> needs a fix --> need swap the dimensions of the image -−> see how to code because maybe not that easy TODO

        # I need to think but not a bad idea!!!




        grp = group(img1, img2, img3, img4, space=INCOMPRESSIBLE_SPACE_TEST/3)

        print('rect',grp.getRect())

        grp.setTopLeft(512, 256) # this seems to work

        print('rect2', grp.getRect())


        img5 = Image2D('/E/Sample_images/counter/05.png')
        img6 = Image2D('/E/Sample_images/counter/06.png')
        img7 = Image2D('/E/Sample_images/counter/07.png')
        img7.set_rotation(180)


        grp2 = group(img5, img6, img7, space=INCOMPRESSIBLE_SPACE_TEST*3)

        grp2.setTopLeft(512, 516)

        print('rect3',grp2.getRect())

        img8 = Image2D('/E/Sample_images/counter/08.png')
        img9 = Image2D('/E/Sample_images/counter/09.png')

        # grp4 = group(img8,img9,orientation='Y')
        grp4 = group(img8,img9,grp,orientation='Y', space=INCOMPRESSIBLE_SPACE_TEST)



# ça marche aussi mais pr je ne sais quelle raison il y a un petit decalage ???
        html_neo = '''
<!DOCTYPE html>
<html>
  <head>
    <title>Font Face</title>
    <style>
      .red {
        color: red;
      }
      .symbol {
        font-family: Symbol;
        font-size: x-large;
      }
      .times-new-roman {
        font-family: "Times New Roman";
        font-size: x-large;
      }
      .verdana {
        font-family: Verdana;
        font-size: x-large;
      }
      .comic-sans-ms {
        font-family: "Comic Sans MS";
        font-size: x-large;
      }
      .wildwest {
        font-family: WildWest;
        font-size: x-large;
      }
      .bedrock {
        font-family: Bedrock;
        font-size: x-large;
      }
    </style>
  </head>
  <body>
    <div class="red">
      <div class="symbol">Symbol</div>
      <div class="times-new-roman">Times New Roman</div>
      <div class="verdana">Verdana</div>
      <div class="comic-sans-ms">Comic Sans MS</div>
      <div class="wildwest">WildWest</div>
      <div class="bedrock">Bedrock</div>
    </div>
  </body>
</html>
        '''

        # html=html_neo # i prefer the old way

        # use the deprecated text size because
        # html = "<font color=blue size=24>this is a test<sup>2</sup><br></font><font color=green size=12>continued<sub>1</sub><br></font><font color=white size=12>test greek <font face='Symbol' size=32>a</font> another &alpha;<font face='Arial' color='Orange'>I am a sentence!</font>"
        text = TAText2D(html)
        text.set_rotation(-45)
        text.color = 0xFF0000 # color does not work !!! --> again needs be fixed !!!
        # text.set_rotation(90)

        t = np.arange(0.0, 2.0, 0.01)
        s = 1 + np.sin(2 * np.pi * t)
        fig, ax = plt.subplots()
        ax.plot(t, s)

        ax.set(xlabel='time (s)', ylabel='voltage (mV)', title=None)
        ax.grid()

        # plt.show()
        # fig.savefig("test.png")
        # plt.show()
        # ça marche --> voici deux examples de shapes
        fig = VectorGraphics2D(fig, x=0, y=0, width=512, height=512)  # could also be used to create empty image with

        # there is a bug !!!!
        # grp5 = group(grp2, grp4,grp, orientation='Y') # ok but pb is they have no same height -−> see how I can fix that --> see how I can set height --> DO I ALWAYS NEED A TARGET HEIGHT OR CAN I TAKE THE SMALLEST OF THE TWO ???
        # grp5 = group(grp2,grp4, orientation=random.choice(['X','Y']), space=INCOMPRESSIBLE_SPACE_TEST, fill_color=0x00FFFF) # ok but pb is they have no same height -−> see how I can fix that --> see how I can set height --> DO I ALWAYS NEED A TARGET HEIGHT OR CAN I TAKE THE SMALLEST OF THE TWO ???
        # grp5 = group(grp2,group(text), grp4, orientation=random.choice(['X','Y']), space=INCOMPRESSIBLE_SPACE_TEST, fill_color=0x00FFFF) # ok but pb is they have no same height -−> see how I can fix that --> see how I can set height --> DO I ALWAYS NEED A TARGET HEIGHT OR CAN I TAKE THE SMALLEST OF THE TWO ???
        grp5 = group(grp2,fig, grp4, orientation=random.choice(['X','Y']), space=INCOMPRESSIBLE_SPACE_TEST, fill_color=0x00FFFF) # ok but pb is they have no same height -−> see how I can fix that --> see how I can set height --> DO I ALWAYS NEED A TARGET HEIGHT OR CAN I TAKE THE SMALLEST OF THE TWO ???

        # I at least managed to display a text but will I manage to get its size and alike
        # text should always be incompressible in fact

        # very good --> it works even with very very complex shapes !!!!

        # see how I can convert this into an xml portable code
        # todo

        # tt marche sublimement

        # TODO --> CHECK HOW TO DO THAT AND WHY IT DOESN'T WORK !!!

        # TODO add bg if desired for the images

        # grp = grp5

        # grp.set_to_size(1024) # do I have a bug here ???
        grp5.setTopLeft(0,0)

        # shall I add <?xml version="1.0" ?>

        if False:
            try:
                xml = object_to_xml(grp5)
                print(xml) # pickle serialization of the object would allow me to implement some sort of a save...

                tst = xml_string_to_object(xml)

                print(tst)
            except Exception:
                traceback.print_exc()

        # small error is likely due to packing --> TODO --> FIX IT

        # here 26 is not enough --> I need a bit more
        # for i in range(26): # even at 100 I get a small imprecision -−> maybe forget about that shit and take 26 always # dirty but ok for now -> I have bigger things to fix --> I tried 100 and it is perfect but 10 already seems to be enough --> maybe that is ok then --> even 3 is ok
        #     grp5.set_to_size(1024) # there is a super tiny misalignment --> is that real or a rounding artifact that would vanish with svg images
        set_to_size(grp5, 1024) # size is incorrect

        print('text size', text.width(), text.height(), text.get_incompressible_size())

        # --> the size is not respected --> there is a bug !!!

        # imprecisionX = grp5[0].getRect().height() - grp5[1].getRect().height()
        # imprecisionY = grp5[0].getRect().width() - grp5[1].getRect().width()
        # imprecision = min(abs(imprecisionX), abs(imprecisionY))
        # print('imprecision in pixels X', imprecisionX)
        # print('imprecision in pixels Y', imprecisionY)
        # print('imprecision ', imprecision)
        get_imprecision(grp5)


        print(grp5.orientation)
        print(grp5.get_incompressible_size())
        print(grp5.get_incompressible_size(axis=grp5.orientation))

        print(grp5.getRect())  # --> marche pas car 668.9099254763324 (0.0, 0.0, 237.55105999039787, 668.9099254763324) --> small bug somewhere  --> size is ok if no space --> the pb comes from the space --> need a fix that is very smart

        print('####INSIDE####')
        for elm in grp5:
            print(elm.getRect())

        preview(grp5) # pb this causes the soft to exit --> I need make it modal or alike --> think of that




        # I may need to dissect the components
        # if this is an incompressible shit then setting all spaces to 0 would do the job !!



        # very good it handles spaces too --> very good







        # see how I can handle figures ???? --> I would need a smart stuff
        # see how I can generate the file !!! --> TODO






        if False:
            # do all of it



            # # grp = group(img1)
            #
            grp3 = group(grp, grp2, orientation='Y')

            # what happens if I add a group to another group -−> can I resize it and how will it determine the optimal size


            # can a row contain a group --> see
            # maybe I need the y ratio or the x and the incompressible height or width --> TODO







            # grp3 = group(grp, grp2, orientation='X')


            # I am not very far apparently in Y --> am I doing a mistake ???? --> is that due to errors in incompressible stuff

            # it roughly seems to work

            # but is all of this working ???




            print('rect4', grp.getRect(), 'rect5',grp2.getRect())

            grp = grp3




        # grp2.setTopLeft(512,256)
        # grp2=grp

        # grp = grp2

        # each group is ok but they cannot be combined
        # --> see what causes the bug

        # shall I force a size on group creation -> force same height to be max height or min height upon creation --> min height is smartest


    # print(grp[0]) # first item
    # print(grp[-1]) # last item
    # print(grp.orientation)
    # print(len(grp))
    #
    # print(grp.width())
    # print(grp.getRect())

    if False:

        start = timer()

        grp.set_to_size(512)
        grp.checkAR()

        end = timer() - start
        print('bounds =', grp.getRect())
        print("elapsed time",end)

        # this is super fast and works super well --> I have my killer app...

    grp.orientation='Y'
    start = timer()

    # grp.set_to_size(512)
    # grp.checkAR()

    end = timer() - start
    print('bounds =', grp.getRect())
    print("elapsed time2", end)
    # grp.check()

    # print(bounding_rect)

    # very good --> I can access all the stuff in one go -> very cool

    # very good --> all seems good

    # group can be groups of images or of stuff

    # see all I can do...
    # all is ok now !!!
    # all is good !!!

    # very good --> now try to do the same with images and plot them --> should be easy !!!
    # then add functions to the group

    # maybe offer panels as collections of rows or cols --> probably the simplest and allow empty images or spacers for incomplete panels

    # try to draw

    # TODO --> handle translations ... and alike
    # try to plot groups of groups

    preview(grp)
