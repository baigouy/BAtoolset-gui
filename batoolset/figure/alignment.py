# align objects left right top or bottom
# maybe just need methods and not even a class
# logger
import os


from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from deprecated import deprecated
from qtpy.QtCore import QRectF

from batoolset.drawings.shapes.point2d import Point2D
from batoolset.tools.logger import TA_logger
import numpy as np

logger = TA_logger()

# TODO replace all functions by that to avoid duplicated code

# def setToWidth(space, width_in_px, *objects):
#     if width_in_px is None:
#         return
#     bounds = updateBoudingRect(*objects)
#     left = Point2D(bounds.topLeft())
#     incompressible_width = 0
#     for img in objects:
#         incompressible_width+=img.getIncompressibleWidth()
#     # si row doit maintenir same height until reached desired width is reached --> change its width --> doit aussi connaitre la incompressible height des objects
#     pure_image_width = (bounds.width()) - incompressible_width
#     # print(width_in_px, self.getIncompressibleWidth(), (nb_cols - 1.) * self.space )
#     width_in_px -= incompressible_width
#     ratio = width_in_px / pure_image_width
#     for img in objects:
#         img.setToWidth(img.boundingRect().width() * ratio)
#     packX(space, left, *objects)
#     # self.updateBoudingRect()

# def setToHeight2(space, height_in_px, *objects):
#     if height_in_px is None:
#         return
#     bounds = updateBoudingRect(*objects)
#     left = Point2D(bounds.topLeft())
#     incompressible_height = 0
#     for img in objects:
#         incompressible_height+=img.getIncompressibleHeight()
#     # si row doit maintenir same height until reached desired width is reached --> change its width --> doit aussi connaitre la incompressible height des objects
#     pure_image_height = (bounds.height()) - incompressible_height
#     # print(width_in_px, self.getIncompressibleWidth(), (nb_cols - 1.) * self.space )
#     height_in_px -= incompressible_height
#     ratio = height_in_px / pure_image_height
#     for img in objects:
#         img.setToHeight(img.boundingRect().height() * ratio)
#     packY(space, left, *objects)
#     # self.updateBoudingRect()



#from timeit import default_timer as timer see why so slow --> see what part of computation is slow and remove it
def setToHeight(space, height_in_px, *objects):
    if height_in_px is None:
        return
    bounds = updateBoudingRect(*objects)
    left = Point2D(bounds.topLeft())
    for img in objects:
        img.setToHeight(height_in_px)
    packX(space, left, *objects)
    # self.updateBoudingRect()

def _brute_force_find_width(col1, min_h, max_h, increment, desired_height):
    # to be faster --> find sign inversion and stop there and take closest
    # stop on sign change in fact
    closest = None
    mn = 100000000
    old_sign = None
    break_soon = False


    for width in np.arange(min_h, max_h, increment):
        col1.setToWidth(width)
        # print('bob', height, col1.width(), col1.height())
        # in fact before that it becomes <0

        if old_sign is not None:
            if old_sign > 0 and col1.height() - desired_height < 0:
                # print('changing sign --> stopping')
                break_soon = True
            elif old_sign < 0 and col1.height() - desired_height > 0:
                # print('changing sign --> stopping')
                break_soon = True

        if old_sign is None:
            if col1.height() - desired_height < 0:
                old_sign = -1
            else:
                old_sign = 1
        if (col1.height() - desired_height) <= mn and col1.height() - desired_height >= 0:
            closest = (col1.width(), col1.height(), width)
            mn = col1.height() - desired_height
            if break_soon:
                # print('stopping at ',height)  # stopping at  41.14420004379321 min_h, max_h 40.14420004379321 43.19553376948639 # --> a vraiment stoppé vite en fait
                break

    # print('break_soon, closest, min_h, max_h, increment',break_soon, closest, min_h, max_h, increment)
    return closest


def _brute_force_find_height(col1, min_h, max_h, increment, desired_width):
        # to be faster --> find sign inversion and stop there and take closest
        # stop on sign change in fact
        closest = None
        mn = 100000000
        old_sign = None
        break_soon = False
        for height in np.arange(min_h, max_h, increment):
            col1.setToHeight(height)
            # print('bob', height, col1.width(), col1.height())
            # in fact before that it becomes <0

            if old_sign is not None:
                if old_sign > 0 and col1.width() - desired_width < 0:
                    # print('changing sign --> stopping')
                    break_soon = True
                elif old_sign < 0 and col1.width() - desired_width > 0:
                    # print('changing sign --> stopping')
                    break_soon = True

            if old_sign is None:
                if col1.width() - desired_width < 0:
                    old_sign = -1
                else:
                    old_sign = 1
            if (col1.width() - desired_width) <= mn and col1.width() - desired_width >= 0:
                closest = (col1.width(), col1.height(), height)
                mn = col1.width() - desired_width
                if break_soon:
                    # print('stopping at ',height)  # stopping at  41.14420004379321 min_h, max_h 40.14420004379321 43.19553376948639 # --> a vraiment stoppé vite en fait
                    break
        return closest

def setToWidth2(space, width_in_px, *objects):
    if width_in_px is None:
        return
    bounds = updateBoudingRect(*objects)
    left = Point2D(bounds.topLeft())
    for img in objects:
        img.setToWidth(width_in_px)
    packY(space, left, *objects)



def updateBoudingRect(*objects):

    # print('objects',objects)

    if not objects:
        return
    '''updates the image bounding rect depending on content'''
    bounding_rect = QRectF()
    x = None
    y = None
    x2 = None
    y2 = None
    for img in objects:
        topLeft = img.topLeft()
        if x is None:
            x = topLeft.x()
        if y is None:
            y = topLeft.y()
        x = min(topLeft.x(), x)
        y = min(topLeft.y(), y)

        # print(img, img.boundingRect(), type(img))
        # print(img, img.boundingRect(), type(img), img.boundingRect().height())


        if x2 is None:
            try:
                x2 = topLeft.x() + img.get_raw_size()[1]
            except:
                x2 = topLeft.x() + img.boundingRect().width()
        if y2 is None:
            try:
                y2 = topLeft.y() + img.get_raw_size()[0]
            except:
                y2 = topLeft.y() + img.boundingRect().height()
        x2 = max(topLeft.x() + img.boundingRect().width(), x2)
        y2 = max(topLeft.y() + img.boundingRect().height(), y2)

    # print('x, x2, y, y2',x, x2, y, y2)

    bounding_rect.setX(x)
    bounding_rect.setY(y)
    bounding_rect.setWidth(x2 - x)
    bounding_rect.setHeight(y2 - y)
    return bounding_rect



packing_modes = ['X','Y', '-X', '-Y']

# def pack2(space=3, mode=packing_modes[0], *objects_to_pack): # a cleaned and better version of packX
#     if objects_to_pack is None or len(objects_to_pack) <= 1:
#         logger.warning("Nothing to align...")
#         return
#
#     reference = objects_to_pack[0]
#
#     # factor = 1
#     # if '-' in mode:
#     #     factor=-1
#         # last = -last
#
#     if mode == packing_modes[1]:
#         last = reference.y()+reference.height(all=True) # NB I COULD REPLACE topLeft with .topleft
#     else:
#         last = reference.x() + reference.width(all=True)
#
#     # print('last',last, space, reference.y(), reference.height(), reference.height(all=True))
#
#     for img in objects_to_pack[1:]:
#             # img = objects_to_pack[i]
#
#             # print('cur obj', img, type(img))
#             # if i != 0:
#             last += space
#             if mode == packing_modes[1]:
#                 img.setTopLeft(img.x(), last) # here again it could be replaced by setTopLeft
#                 last = img.y() + img.height(all=True)
#             else:
#                 img.setTopLeft(last, img.y())  # here again it could be replaced by setTopLeft
#                 last = img.x() + img.width(all=True)

def pack2(space=3, mode=packing_modes[0], extra_border_mode=False, *objects_to_pack): # a cleaned and better version of packX
    from batoolset.drawings.shapes.image2d import Image2D

    # check position



    # TODO --> allow positioning from

    if objects_to_pack is None or len(objects_to_pack) <= 1:
        # logger.warning("Nothing to align...")
        return

    if mode is None:
        logger.warning("Unknown alignment mode")
        return

    reference = objects_to_pack[0]

    # print('mode', mode)

    if mode not in packing_modes:
        if isinstance(mode, str):
            # tolerate legacy quoted strings ('"X"') from old .pyf files
            mode = mode.strip().strip('\'"')
        if mode not in packing_modes:
            try:
                mode = mode.get_packing_orientation()
            except AttributeError:
                logger.warning('Unknown packing mode ' + repr(mode) + ' --> ignoring')
                return

    if mode is None:
        # logger.warning("Unknown orientation --> ignoring")
        # this is not a known orientation --> skip it
        return


    # print('updated position', mode)

    # factor = 1
    # if '-' in mode:
    #     factor=-1
    #     # last = -last

    orientation = mode.replace('-','')

    if orientation == packing_modes[1]:
        last = reference.y()+reference.height(all=True) if not '-' in mode else 0 # NB I COULD REPLACE topLeft with .topleft
        if extra_border_mode and isinstance(reference, Image2D):
            extra = reference.get_extra_border_size()
            if '-' in mode:
                last-=extra
            else:
                last += extra
    else:
        # try:
        last = reference.x() + reference.width(all=True) if not '-' in mode else 0
        # except:
        #     pass
        if extra_border_mode and isinstance(reference, Image2D):
            extra = reference.get_extra_border_size()
            if '-' in mode:
                last-=extra
            else:
                last += extra

    # print('last',last, space, reference.y(), reference.height(), reference.height(all=True))

    previous_coords = reference.topLeft()
    for img in objects_to_pack[1:]:
            # img = objects_to_pack[i]

            # print('cur obj', img, type(img))
            # if i != 0:
            last += space
            if orientation == packing_modes[1]:
                if not '-' in mode:
                    if extra_border_mode and isinstance(img, Image2D):
                        last+=img.get_extra_border_size()
                    img.setTopLeft(img.x(), last) # here again it could be replaced by setTopLeft
                    last = img.y() + img.height(all=True)
                    if extra_border_mode and isinstance(img, Image2D):
                        last+=img.get_extra_border_size()
                else:
                    last = previous_coords.y() - img.height(all=True)
                    if extra_border_mode and isinstance(img, Image2D):
                        last-=img.get_extra_border_size()
                    img.setTopLeft(img.x(), last)  # here again it could be replaced by setTopLeft
                    if extra_border_mode and isinstance(img, Image2D):
                        last-=img.get_extra_border_size()

            else:
                if not '-' in mode:
                    if extra_border_mode and isinstance(img, Image2D):
                        last-=img.get_extra_border_size()
                    img.setTopLeft(last, img.y())  # here again it could be replaced by setTopLeft
                    last = img.x() + img.width(all=True)
                    if extra_border_mode and isinstance(img, Image2D):
                        last+=img.get_extra_border_size()
                else:
                    if extra_border_mode and isinstance(img, Image2D):
                        last-=img.get_extra_border_size()
                    last = previous_coords.x() - img.width(all=True)
                    if extra_border_mode and isinstance(img, Image2D):
                        last-=img.get_extra_border_size()
                    img.setTopLeft(last, img.y())  # here again it could be replaced by setTopLeft

            previous_coords = img.topLeft()

# new version (cleaner or the packing code!!!)
@deprecated(reason="will switch to pack2 soon")
def pack(space=3, mode=packing_modes[0], *objects_to_pack): # a cleaned and better version of packX
    if objects_to_pack is None or len(objects_to_pack) <= 1:
        # logger.warning("Nothing to align...")
        return

    reference = objects_to_pack[0]

    if mode == packing_modes[1]:
        last = reference.y()+reference.height() # NB I COULD REPLACE topLeft with .topleft
    else:
        last = reference.x() + reference.width()

    for img in objects_to_pack[1:]:
            # img = objects_to_pack[i]
            # if i != 0:
            last += space
            if mode == packing_modes[1]:
                img.setTopLeft(img.x(), last) # here again it could be replaced by setTopLeft
                last = img.y() + img.height()
            else:
                img.setTopLeft(last, img.y())  # here again it could be replaced by setTopLeft
                last = img.x() + img.width()


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'pack' instead.")
def packX(space=3, reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    last_x = reference.topLeft().x()+reference.width() # NB I COULD REPLACE topLeft with .topleft
    # last_y = reference.topLeft().y()

    for i in range(len(objects_to_align_with_respect_to_ref)):
            if i == 0 and skip_first:
                continue
            img = objects_to_align_with_respect_to_ref[i]
            # print('begin', last_x)
            if i != 0:
                last_x += space


            # print('before', last_x, img.boundingRect(), space)
            img.setTopLeft(last_x, img.topLeft().y()) # here again it could be replaced by setTopLeft
            # print(img.boundingRect(), last_x, img.topLeft().x())
            last_x = img.boundingRect().x() + img.boundingRect().width()
            # print('end', last_x)
    # self.updateBoudingRect()

    # align everything with respect to ref
    # get first point and align so that the all have the same x

ORIENTATION_TOP_TO_BOTTOM = 0
ORIENTATION_BOTTOM_TO_TOP = 1

# need do a code for two orientations --> from top to bottom and reverse --> can be useful to do...

@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'pack' instead.")
def packYreverse(space=3, reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()
    last_y = reference.topLeft().y()

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]
        if i != 0:
            last_y -= space
            # last_y -= img.boundingRect().height()
        # print(last_y, img.topLeft())
        img.setTopLeft(img.topLeft().x(), last_y-img.boundingRect().height())
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        x = img.boundingRect().x()
        y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        last_y = img.boundingRect().y()
    # self.updateBoudingRect()


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'pack' instead.")
def packY(space=3, reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()
    last_y = reference.topLeft().y() + reference.height()

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]
        if i != 0:
            last_y += space
        # print(last_y, img.topLeft())
        img.setTopLeft(img.topLeft().x(), last_y)
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        x = img.boundingRect().x()
        y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


    # align everything with respect to ref
    # get first point and align so that the all have the same x

    # align everything with respect to ref
    # get first point and align so that the all have the same x

align_positions = ['Top', 'Bottom','Left', 'Right', 'CenterV', 'CenterH']

# I had to add scale to it to make it much better!!!
def align2(position=None,*objects_to_align_with_respect_to_ref):
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) <=1:
        # logger.warning("Nothing to align...")
        return

    reference = objects_to_align_with_respect_to_ref[0]
    # TOD REPLACE BY A SWITCH --> somehow switch does not work with external variable --> maybe try still

    if position == align_positions[0] or position is None:
        last_y = reference.y()
    elif position == align_positions[1]:
        last_y = reference.y() + reference.height(all=True)
    elif position == align_positions[2]:
        last_x = reference.x()
    elif position == align_positions[3]:
        last_x = reference.x()+reference.width(all=True)
    elif position == align_positions[4]:
        last_y = reference.y() + reference.height(all=True) / 2.  # should be the end point of every stuff
    elif position == align_positions[5]:
        last_x = reference.x() + reference.width(all=True) / 2.
    else:
        pass
    for img in objects_to_align_with_respect_to_ref[1:]:
        if position == align_positions[0] or position is None:
            img.setTopLeft(img.x(), last_y)
        elif position == align_positions[1]:
            pos_y = img.y() + img.height(all=True)
            difference_y = last_y - pos_y
            img.setTopLeft(img.x(), img.y() + difference_y)
        elif position == align_positions[2]:
            img.setTopLeft(last_x, img.y())
        elif position == align_positions[3]:
            pos_x = img.x() + img.width(all=True)
            difference_x = last_x - pos_x
            img.setTopLeft(img.x() + difference_x, img.y())
        elif position == align_positions[4]:
            pos_y = img.y() + img.height(all=True) / 2.
            difference_y = last_y - pos_y
            img.setTopLeft(img.x(), img.y() + difference_y)
        elif position == align_positions[5]:
            pos_x = img.x() + img.width(all=True) / 2.
            difference_x = last_x - pos_x
            img.setTopLeft(img.x() + difference_x, img.y())
        else:
            print('error trying to align there')
            pass


# this is the new version of the align code that is not duplicated and so much better
@deprecated(reason='will soon switch to align2')
def align(position=None,*objects_to_align_with_respect_to_ref):
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) <=1:
        # logger.warning("Nothing to align...")
        return

    reference = objects_to_align_with_respect_to_ref[0]
    # TOD REPLACE BY A SWITCH --> somehow switch does not work with external variable --> maybe try still

    if position == align_positions[0] or position is None:
        last_y = reference.y()
    elif position == align_positions[1]:
        last_y = reference.y() + reference.height()
    elif position == align_positions[2]:
        last_x = reference.x()
    elif position == align_positions[3]:
        last_x = reference.x()+reference.width()
    elif position == align_positions[4]:
        last_y = reference.y() + reference.height() / 2.  # should be the end point of every stuff
    elif position == align_positions[5]:
        last_x = reference.x() + reference.width() / 2.
    else:
        pass
    for img in objects_to_align_with_respect_to_ref[1:]:
        if position == align_positions[0] or position is None:
            img.setTopLeft(img.x(), last_y)
        elif position == align_positions[1]:
            pos_y = img.y() + img.height()
            difference_y = last_y - pos_y
            img.setTopLeft(img.x(), img.y() + difference_y)
        elif position == align_positions[2]:
            img.setTopLeft(last_x, img.y())
        elif position == align_positions[3]:
            pos_x = img.x() + img.width()
            difference_x = last_x - pos_x
            img.setTopLeft(img.x() + difference_x, img.y())
        elif position == align_positions[4]:
            pos_y = img.y() + img.height() / 2.
            difference_y = last_y - pos_y
            img.setTopLeft(img.x(), img.y() + difference_y)
        elif position == align_positions[5]:
            pos_x = img.x() + img.width() / 2.
            difference_x = last_x - pos_x
            img.setTopLeft(img.x() + difference_x, img.y())
        else:
            pass

        # match position:
        #     case align_positions[0]:
        #         pass
        #     case align_positions[1]:
        #         pass
        #     case pattern-3:
        #         pass
        #     case _:
        #         pass




@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
def alignLeft(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    last_x = reference.topLeft().x()
    # last_y = reference.topLeft().y()

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]

        img.setTopLeft(last_x, img.topLeft().y())
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
def alignTop(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()
    last_y = reference.topLeft().y()

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]

        img.setTopLeft(img.topLeft().x(), last_y)
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


    # align everything with respect to ref
    # get first point and align so that the all have the same x


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
def alignBottom(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()
    last_y = reference.topLeft().y()+reference.height() # should be the end point of every stuff

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]


        pos_y = img.topLeft().y()+img.height()
        difference_y = last_y-pos_y
        img.setTopLeft(img.topLeft().x(), img.topLeft().y()+difference_y)
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


    # align everything with respect to ref
    # get first point and align so that the all have the same x


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
# bug here now with the images
def alignRight(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    last_x = reference.topLeft().x()+reference.width() # should be the end point of every stuff
    # last_y = reference.topLeft().y()+reference.height() # should be the end point of every stuff

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]

        pos_x = img.topLeft().x()+img.width()
        difference_x = last_x-pos_x
        img.setTopLeft(img.topLeft().x()+difference_x, img.topLeft().y())
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


    # align everything with respect to ref
    # get first point and align so that the all have the same x


@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
def alignCenterH(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()+reference.width()/2. # should be the end point of every stuff
    last_x = reference.topLeft().x()+reference.width()/2. # should be the end point of every stuff
    # last_y = reference.topLeft().y()+reference.height() # should be the end point of every stuff

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]

        pos_x = img.topLeft().x()+img.width()/2.
        difference_x = last_x-pos_x
        img.setTopLeft(img.topLeft().x()+difference_x, img.topLeft().y())
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()


    # align everything with respect to ref
    # get first point and align so that the all have the same x

@deprecated(reason="This method is deprecated and will be removed in the future. Please use 'align' instead.")
def alignCenterV(reference=None, *objects_to_align_with_respect_to_ref):
    skip_first = False
    if objects_to_align_with_respect_to_ref is None or len(objects_to_align_with_respect_to_ref) == 0:
        # logger.warning("Nothing to align...")
        return
    if reference is None:
        if len(objects_to_align_with_respect_to_ref) < 2:
            logger.warning("Reference is None, can't align anything...")
            return
        else:
            reference = objects_to_align_with_respect_to_ref[0]
            skip_first = True
            # del objects_to_align_with_respect_to_ref[0]

    # last_x = reference.topLeft().x()
    last_y = reference.topLeft().y()+reference.height()/2. # should be the end point of every stuff

    for i in range(len(objects_to_align_with_respect_to_ref)):
        if i==0 and skip_first:
            continue
        img = objects_to_align_with_respect_to_ref[i]


        pos_y = img.topLeft().y()+img.height()/2.
        difference_y = last_y-pos_y
        img.setTopLeft(img.topLeft().x(), img.topLeft().y()+difference_y)
        # get all the bounding boxes and pack them with desired space in between
        # get first point and last point in x
        # x = img.boundingRect().x()
        # y = img.boundingRect().y()
        # last_x = img.boundingRect().x() + img.boundingRect().width()
        # last_y = img.boundingRect().y() + img.boundingRect().height()
    # self.updateBoudingRect()
