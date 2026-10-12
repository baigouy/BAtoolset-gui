# try to find a code that finds the new scaling so that the image fits to the new size
# assume all images have the same height in a row and the same width in a column

# can I not even store everything as a big numpy array ???

# test with 3 rectangles

# keep AR the same --> need just apply a scaling to the image and in fact to all images the same, by the way

#
# def find_scaling_to_fit():
#     incompressible_length = (len(widths)-1)*space_between_images
#     image_width_to_fit_not_counting_incompressible_length = final_width-incompressible_length
#     sum_individual = sum(widths)
#     common_scaling = image_width_to_fit_not_counting_incompressible_length/sum_individual
#
#     print(common_scaling)
#
#     # print(widths*common_scaling)
#     corrected_widths = [w*common_scaling for w in widths]
#     print(widths)
#     print(corrected_widths)
#     print(sum(corrected_widths))
#     print(sum(corrected_widths)+incompressible_length)
#     print(incompressible_length)
#     # print()

    # ça marche super en fait et c'est vraiment facile

# computes the rescaling factor so that images get rescaled to fit the desired dimension --> much smarter that way than using brute force!!!

import os
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
import sys
from qtpy import QtWidgets
from qtpy.QtCore import QRectF


# nb the pb asssumes AR is kept constant which is true for images but not with panels containing images and incompressible space between them --> need some extra computation then


common_value = 0


def get_common_scaling_factor(dimensions_in_the_desired_dimension, desired_final_size, size_of_incompressible_elements_in_dimension=3):
    incompressible_length = (len(dimensions_in_the_desired_dimension) - 1) * size_of_incompressible_elements_in_dimension
    image_width_to_fit_not_counting_incompressible_length = desired_final_size - incompressible_length
    sum_individual = sum(dimensions_in_the_desired_dimension)
    common_scaling = image_width_to_fit_not_counting_incompressible_length / sum_individual

    # print(common_scaling)

    # print(widths*common_scaling)
    # corrected_widths = [w * common_scaling for w in dimensions_in_the_desired_dimension]
    # print(dimensions_in_the_desired_dimension)
    # print(corrected_widths)
    # print(sum(corrected_widths))
    # print(sum(corrected_widths) + incompressible_length)
    # print(incompressible_length)

    return common_scaling

#########################################################KEEP EQUATIONS TO SOLVE THE CHANGE IN SIZE
# final_width = width_obj1 + width_obj2+ width_obj3 + (nb_of_objs-1)*space
# new_width = new_width_obj1 + new_width_obj2+ new_width_obj3 + (nb_of_objs-1)*space
# new_width = width_obj1*scaling + new_width_obj2*scaling+ new_width_obj3*scaling + (nb_of_objs-1)*space
# height = same whatever the condition but can change --> need solve the equa so that height is the same while width obeys the new stuff
# heightA = heightB = heightC # always
# comment relier la width à la height ???

# final_AR = widthA/heightA = (incomp_widthA+widthA_non_incom)/(incomp_heightA+heightA_non_incom)
# heightA =(incomp_heightA+heightA_non_incom)
# widthA = (incomp_widthA+withA_non_incom)
# AR = withA_non_incom/heightA_non_incom
# heightA_non_incomp = widthA_non_incomp/AR
# heightA = incomp_heightA+(widthA_non_incomp/AR)
# widthA = (incomp_widthA+withA_non_incom)
# --> with that can I compute the best change for all
# final_AR = ((scaling_x*current_widthA) +widthA_non_incom)/((scaling_y*current_heightA)+heightA_non_incom)
# new_widthA = ((scaling_xA*current_widthA) +widthA_non_incom)
# new_heightA = ((scaling_yA*current_heightA)+heightA_non_incom)
# I need find both scalings at the same time
# reorder equa for scaling -> TODO
# scaling_xA = (new_widthA - widthA_non_incom)/current_widthA
# scaling_yA = (current_heightA - heightA_non_incom)/current_heightA
# need find both so that everything fits
# --> easy in fact and that is what I need to have
# height is always related to width too given the incompressible AR ratio --> YES IN FACT IT MUST BE
# heightA = heightB = heightC # whatever happens the images all have the same height in a row
# so by definition
# height A is fixed but yet to an unknown value
# heightA = heightB = heightC
# width is fixed and height must be adjusted but the same in all cases
# --> how does one compute that
# that must be doable but complex
# j'ai 6 inconnues --> mes scalings en x et en y et j'ai une taille constante pour un et une egalite pour l'autre
#


# final AR = ((scalingx * old_compressible_dim_x)+incomp x)/((scalingy * old_compressible_dim_y)+incomp y)) =  ((scalingx * old_compressible_dim_x)+incomp x)/((scalingy * (old_compressible_dim_x/AR))+incomp y))
# finalAR = final_dimx/final dimy
# final_dimx/final dimy = ((scalingx * old_compressible_dim_x)+incomp x)/((scalingy * (old_compressible_dim_x/AR))+incomp y))
# final_dimx = final dimy* (((scalingx * old_compressible_dim_x)+incomp x)/((scalingy * (old_compressible_dim_x/AR))+incomp y)))
# final_dimy = final dimx/(((scalingx * old_compressible_dim_x)+incomp x)/((scalingy * (old_compressible_dim_x/AR))+incomp y)))
# final_dimy1 = final_dimy2 =final_dimy3
# the early things are known and either the final height or width is known --> not true but i know they are eaqual --> so I can solve it
# and get all the parameters

# sum of dims + sum incomp = desired width
# sum(incomp)+sum(images) = desired_width
# I need get the 3 heights that would fulfill the criterion I want


# same height --> ????
# how do I do that






# faire ça

# start with just two images and solve it
# heightA = heightB
# final_width = widthA + widthB + incomp_width
# need find widthA and widthB so that the heights are the same
# final_width = scalingxA * original_widthA +scalingxB * original_widthB  + incomp_width
# final_height = scalingyA * original_heightA+scalingyB * original_heightB
# how can I relate width and height
# final_AR is unknown

# in fact I don't find any other way than brute force but there has to be a way ??? --> too bad I forgot my basic math classes
# ratio = sizex/sizey --> ce n'est pas fixe mais ça depend des
# the pb is that this ratio is unknown


# height +  ((leny-1)*space) = AR*width + ((lenx-1)*space)
# height = AR*width + ((lenx-1)*space)-  ((leny-1)*space)
# heights of the three should be equal --> can compute
# y = ax+b # image1 --> what I want is a ???
# y = dx'+c
# all same height
#dx'+c = ax+b
# sum of width = fixed size
# dx'+c + ax+b= 512
# c and b are fixed
# dx'+ax = 512-c-b # --> equation 1
# need another equation
# need find d and b
# est ce que c'est ça ???
# https://calculis.net/systeme-n-equations#solutions

# dx'+c = ax+b
# d = (ax+b-c)/x'
# a = (dx'+c-b)/x
# deux equations à deux inconnues
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html or that ???
# https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html # or that

# or solve for different heights
# y1 = a1*x1+b1
# y2 = a2*x2+b2
# y1 = y2
# a1x1 = a2*x2+b1-b2
# a1*x1+b1 + a2*x2+b2 + c = 512
# https://www.youtube.com/watch?v=QkkpcVbNLVE --> je pense que c'est ce que je cherche
# du coup voir comment le resoudre pratiquement
# or brute force solve it numerically
# see the smart and fastest way to do that
# i need find a1 and x1 and a2 and x2 -> need another equation then



# autre solution faire usr un systeme packé et le changer en non packé --> marche si et seulement si le truc est incompressible dans une seule dimension
#


















#########################################################KEEP EQUATIONS TO SOLVE THE CHANGE IN SIZE

# worst case --> I can brute force it a bit but I would love not to
# or need a post process correction to fit in same height but pb is that it will also change width and therefore I will have trouble beacuse it will change width and I will need do that recursively until I reach the global minima
# -> think about it
# think about it

# AR = (real_width + incomp_width)/(real_height + incomp_height)
# incomp_width =
# width = sum_width_objects
# probably easy --> I just need to have in the formula the AR
# it should fit in the given space
# if same size --> incompressible fits
def get_common_scaling_factor_taking_incompressibility_into_account(dimensions_in_the_desired_dimension, desired_final_size, size_of_incompressible_elements_in_dimension=3):
    incompressible_length = (len(dimensions_in_the_desired_dimension) - 1) * size_of_incompressible_elements_in_dimension
    image_width_to_fit_not_counting_incompressible_length = desired_final_size - incompressible_length
    sum_individual = sum(dimensions_in_the_desired_dimension)
    common_scaling = image_width_to_fit_not_counting_incompressible_length / sum_individual

    # print(common_scaling)

    # print(widths*common_scaling)
    # corrected_widths = [w * common_scaling for w in dimensions_in_the_desired_dimension]
    # print(dimensions_in_the_desired_dimension)
    # print(corrected_widths)
    # print(sum(corrected_widths))
    # print(sum(corrected_widths) + incompressible_length)
    # print(incompressible_length)

    return common_scaling

def get_master_bounds2(group_of_shapes):
    # from batoolset.drawings.shapes.group import Group
    bounds = QRectF()

    if group_of_shapes is None:
        return bounds
    max_width = 0
    max_height = 0
    min_x=100000000
    min_y=100000000

    for shape in group_of_shapes:
        # if isinstance(shape, Group):
        #     rect = shape.getRect()
        # else:
        #     rect = shape.getRect(all=True)
        rect = shape.getRect(all=True)
        max_width = max(max_width, rect.x()+rect.width())
        max_height = max(max_height, rect.y()+rect.height())
        min_x = min(min_x, rect.x())
        min_y = min(min_y, rect.y())
    bounds.setX(min_x)
    bounds.setY(min_y)
    bounds.setWidth(max_width-min_x)
    bounds.setHeight(max_height-min_y)



    return bounds
#
# gets the master rect of a list of objects
# Nb should I allow negative bounds ??? --> maybe not in fact
# def get_master_bounds(group_of_shapes):
#     bounds = QRectF()
#     max_width = 0
#     max_height = 0
#     for shape in group_of_shapes:
#        # rect = shape.boundingRect()
#        rect = shape.getRect(all=True)
#        max_width = max(max_width, rect.x()+rect.width())
#        max_height = max(max_height, rect.y()+rect.height())
#     bounds.setWidth(max_width)
#     bounds.setHeight(max_height)
#
#     # print('master rect detected', bounds)
#
#     return bounds



if __name__ == '__main__':

    # ça marche mais c'est super slow -> can i make it faster then ???


    if True:
        # test solving equation
        import numpy as np
        pass