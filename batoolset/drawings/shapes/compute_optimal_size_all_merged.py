from batoolset.drawings.shapes.rectangle2d import Rectangle2D
# from PyQt5.QtCore import QRectF, QSizeF
from qtpy.QtCore import QRectF, QSizeF

# def resize_rect_preserve_aspect_ratio(rect: Rectangle2D, new_height: float):
#     current_width = rect.width()
#     current_height = rect.height()
#     aspect_ratio = current_width / current_height
#
#     new_width = aspect_ratio * new_height
#     # new_rect = Rectangle2D(QRectF(rect.x(), rect.y(), new_width, new_height)) # here I rather need to scale the rect
#     # rect.set_to_scale(aspect_ratio)
#     # dirty hack for test
#     # rect = Rectangle2D(rect)
#
#     # print(current_width, new_width)
#
#     rect.set_to_scale(current_width/new_width)
#
#     return rect




# TODO --> fuse all of this in a single super smart stuff




# can I use my own LLM there ???


def resize_rect_preserve_aspect_ratio(rect: Rectangle2D, new_width: float, new_height:float):
    # I guess the bug is there
    current_width = rect.width()
    current_height = rect.height()


    # if current_height == 0:
    #     return rect
    # print(current_height)
    aspect_ratio = float(current_width) / float(current_height)

    # very good --> so I could fix it
    if new_height is not None:
    # if False: # this is to favor height
    #     new_height = new_size.height()
        # # new_width = aspect_ratio * new_height if aspect_ratio < new_size.width() / new_size.height() else new_size.width() * current_height / current_width
        new_width = aspect_ratio * new_height
        rect.set_to_scale(1./(new_width/current_width))
    else:
        # new_width = new_size.width()
        new_height = new_width/aspect_ratio
        rect.set_to_scale(1./(new_height / current_height)) # TODO --> clean this code --> make it better

    # new_rect = QRectF(rect.x(), rect.y(), new_width, new_height)
    # return new_rect
    return rect


def resize_rects(rects: list, target_width:float, target_height: float):
    resized_rects = []
    for rect in rects:
        resized_rect = resize_rect_preserve_aspect_ratio(rect, target_width, target_height)
        resized_rects.append(resized_rect)

    return resized_rects

# I need get its size set its scale to 1 get just the text size yet crop the
def resize_incompressible_rects(rects: list, target_width:float, target_height: float):
    # max_w = 0
    # max_h = 0
    # failed_images = []
    # text_images = []
    # individual_width = []
    # individual_height = []
    # for elm in self.paint.EZFIG_panel.selected_shape:
    #     try:
    #         print(elm, elm.annotations, elm.annotations[0], elm.annotations[0].width(all=True),
    #               elm.annotations[0].height(all=True))
    #         if len(elm.annotations) != 1:
    #             raise Exception('not good')
    #         individual_width.append(elm.annotations[0].width(all=True))
    #         individual_height.append(elm.annotations[0].height(all=True))
    #         max_w = max(elm.annotations[0].width(all=True), max_w)
    #         max_h = max(elm.annotations[0].height(all=True), max_h)
    #         text_images.append(elm)
    #     except:
    #         # pass # if fails this is not a text image
    #         failed_images.append(elm)  # if image is failed then we have it



    max_w = 0
    max_h = 0
    resized_rects = []
    for rect in rects:
        # resized_rect = resize_rect_preserve_aspect_ratio(rect, target_width, target_height)
        # resized_rects.append(resized_rect)
        txt_width = rect.annotations[0].width(all=True)
        txt_height = rect.annotations[0].height(all=True)
        max_w = max(txt_width, max_w)
        max_h = max(txt_height, max_h)
        # set the texts to their minimal size --> then resize the stuff in the very end so that all fits
        rect.setWidth(txt_width)
        rect.setHeight(txt_height)

    return max_w, max_h, resized_rects

# def calculate_target_width(rects: list, max_total_height: float):
#     total_aspect_ratio = sum(rect.height() / rect.width() for rect in rects if not rect.immutable) # immutable objects should be removed from the stuff -−> TODO
#     target_width = max_total_height / total_aspect_ratio
#     return target_width

# def calculate_target_height(rects: list, max_total_width: float):
#     # in fact if there are incompressible ones here I need
#     total_aspect_ratio = sum(rect.width() / rect.height() for rect in rects if not rect.immutable) # immutable objects should be removed from the stuff -−> TODO
#     target_height = max_total_width / total_aspect_ratio
#     return target_height


# def resize_rects_within_total_width(rects: list, max_total_width: float, space_in_px: float):
#     incompressible_width = (len(rects) - 1) * space_in_px
#     available_width = max_total_width - incompressible_width
#
#     target_height = calculate_target_height(rects, available_width)
#     resized_rects = resize_rects(rects, None, target_height) # --> indeed that works
#
#     return resized_rects

# def resize_rects_within_total_height(rects: list, max_total_height: float, space_in_px: float):
#     incompressible_height = (len(rects) - 1) * space_in_px
#     available_height = max_total_height - incompressible_height
#
#     target_width = calculate_target_width(rects, available_height)
#     resized_rects = resize_rects(rects, target_width,None) # --> indeed that works
#
#     return resized_rects

def resize_rects_within_total_width(rects: list, max_total_width: float, sum_incompressible_space_along_x: float):
    # incompressible_width = (len(rects) - 1) * space_in_px
    available_width = max_total_width - sum_incompressible_space_along_x
    initial_width=available_width

    total_incompressible_text_width = sum(rect.width(all=True) for rect in rects if rect.isText)

    compressible = [rect for rect in rects if not rect.isText]
    incompressible = [rect for rect in rects if rect.isText]

    available_width-=total_incompressible_text_width

    # print('total_incompressible_text_width',total_incompressible_text_width)
    # print(compressible)
    # print(incompressible)

    # target_height = calculate_target_height(rects, available_width)

    # total_aspect_ratio = sum(rect.width() / rect.height() for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO
    # total_aspect_ratio = sum(rect.getAR()for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO
    # total_aspect_ratio = sum(rect.getAR() for rect in rects)  # immutable objects should be removed from the stuff -−> TODO

    # print('final compressible', compressible)

    total_aspect_ratio = sum(rect.getAR() for rect in compressible)  # immutable objects should be removed from the stuff -−> TODO


    # print('total_aspect_ratio modified',total_aspect_ratio)
    # the idea is that I need to fit the non text stuff there



    # if total_aspect_ratio == 0:
    #     print('DEBUG DABU')
    #     for rect in rects:
    #         print('tata', rect.getAR())


    if total_aspect_ratio!=0: # this is just to avoid errors # maybe fit all to current otherwise
        target_height = available_width / total_aspect_ratio
    else:
        target_height = available_width

    # resized_rects = resize_rects(rects, None, target_height) # --> indeed that works
    resized_compressible_rects = resize_rects(compressible, None, target_height) # --> indeed that works

    # if resized_compressible_rects:
    #     target_width, target_height =
    max_w, max_h, resized_incompressible_rects = resize_incompressible_rects(incompressible, None, target_height) # --> indeed that works
    if compressible:
        height = compressible[0].height(all=True)
    else:
        height = max_h
        if incompressible : # incompressible
            sum_of_widths = sum(rect.width(all=True) for rect in incompressible)
            # Compute the scaling factor
            scaling_factor = initial_width / sum_of_widths

            # print('total_aspect_ratio in changed',scaling_factor)
            for elm in incompressible:
                elm.setWidth(elm.width(all=True)*scaling_factor)
                elm.set_to_scale(1.)

    if incompressible:
        for elm in incompressible:
            elm.setHeight(height)
            elm.set_to_scale(1.)


    # last thing to do -> if there is no compressible I need adjust the total size to the deisred by keeping height constant and increasing height
    # by the rescaling factor



    return rects # return all rects that have been modified in original order


def resize_rects_within_total_height(rects: list, max_total_height: float, sum_incompressible_space_along_y: float):
    # incompressible_height = (len(rects) - 1) * space_in_px
    available_height = max_total_height - sum_incompressible_space_along_y
    initial_height=available_height
    total_incompressible_text_height = sum(rect.getRect(all=True).height() for rect in rects if rect.isText)


    # target_width = calculate_target_width(rects, available_height)

    # total_aspect_ratio = sum(rect.height() / rect.width() for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO
    # total_aspect_ratio = sum(rect.getAR(invert=True) for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO

    compressible = [rect for rect in rects if not rect.isText]
    incompressible = [rect for rect in rects if rect.isText]

    available_height -= total_incompressible_text_height

    # print('total_incompressible_text_height', total_incompressible_text_height)
    # print(compressible)
    # print(incompressible)

    # target_height = calculate_target_height(rects, available_width)

    # total_aspect_ratio = sum(rect.width() / rect.height() for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO
    # total_aspect_ratio = sum(rect.getAR()for rect in rects if not rect.immutable)  # immutable objects should be removed from the stuff -−> TODO
    # total_aspect_ratio = sum(rect.getAR() for rect in rects)  # immutable objects should be removed from the stuff -−> TODO


    # total_aspect_ratio = sum(rect.getAR(invert=True) for rect in rects)  # immutable objects should be removed from the stuff -−> TODO
    total_aspect_ratio = sum(rect.getAR(invert=True) for rect in compressible)  # immutable objects should be removed from the stuff -−> TODO

    # print('total_aspect_ratio modified', total_aspect_ratio)

    if total_aspect_ratio != 0:  # this is just to avoid errors # maybe fit all to current otherwise
        target_width = available_height / total_aspect_ratio
    else:
        target_width = available_height

    # target_width = available_height / total_aspect_ratio

    # resized_rects = resize_rects(rects, target_width,None) # --> indeed that works
    resized_compressible_rects = resize_rects(compressible, target_width, None)  # --> indeed that works
    max_w, max_h, resized_incompressible_rects = resize_incompressible_rects(incompressible, target_width,None)  # --> indeed that works
    if compressible:
        width = compressible[0].width(all=True)
    else:
        width = max_w
        if incompressible : # incompressible
            sum_of_heights = sum(rect.height(all=True) for rect in incompressible)
            # Compute the scaling factor
            scaling_factor = initial_height / sum_of_heights

            # print('total_aspect_ratio in chnaged',scaling_factor)
            for elm in incompressible:
                elm.setHeight(elm.height(all=True)*scaling_factor)
                elm.set_to_scale(1.)

    if incompressible:
        for elm in incompressible:
            elm.setWidth(width)
            elm.set_to_scale(1.)

    return rects


def resize_rects_within_grid(rects: list, grid_size: tuple, max_total_width: float, max_total_height: float, incompressible_width: float, incompressible_height: float, fit_in_width:int):
    # this is a bit too complicated with grids as they will have complex incompressibility in width and height that will vary depending on the amount of rows and cols !!!!

    # this sounds like good and simple code!!!
    rows, cols = grid_size

    # rather than passing the incompressible size I just would need to compute it per object on the fly !!!

    available_width = max_total_width - (cols - 1) * incompressible_width # NB maybe this should be done per row ????
    available_height = max_total_height - (rows - 1) * incompressible_height

    target_width = available_width / cols
    target_height = available_height / rows

    if fit_in_width:
        target_height=None
    else:
        target_width=None
    # here I need to choose between width and height
    # ideally always prefer width except if extends beyond height
    # when resized
    # start with width

    # in fact I should take either here --> the best fit in width and or in height -−> auto take it
    # print('sizes',target_width, available_width, max_total_width, target_height, available_height, max_total_height) #92.5 370.0 400 193.33333333333334 580.0 600

    resized_rects = []
    for rect in rects:
        resized_rect = resize_rect_preserve_aspect_ratio(rect, target_width, target_height)
        resized_rects.append(resized_rect)

    return resized_rects



# I could make it smarter by reading the incompressible height from the image and from the packing -−> this is why I need a group maybe???