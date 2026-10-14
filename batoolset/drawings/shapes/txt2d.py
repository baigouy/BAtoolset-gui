# TODO allow text for be written at an angle and determine it size then
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from batoolset.pyqts.tools import get_painter_transform_and_rotation
from batoolset.drawings.shapes.textorientation import get_angle
from batoolset.drawings.shapes.Position import Position
from qtpy import QtCore
from qtpy.QtCore import QRect
from qtpy.QtGui import QTextDocument, QTextOption
from qtpy.QtGui import QPainter, QImage, QColor, QFont, QBrush, QTransform
from qtpy.QtCore import QRectF, QPointF
import sys
from qtpy import QtGui
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QApplication
from batoolset.drawings.shapes.rectangle2d import Rectangle2D
# log errors
from batoolset.tools.logger import TA_logger
logger = TA_logger()

class TAText2D(Rectangle2D):

    # TODO add bg to it so that it can be drawn
    def __init__(self, text=None, doc=None, opacity=1.,x=None, y=None, fill_color=None, color=None, text_orientation='X',placement=Position(),range=None, is_letter=False,__version=1.0,*args, **kwargs):
        if doc is not None and isinstance(doc, QTextDocument):
            self.doc = doc
            self.doc.setDocumentMargin(0)  # important so that the square is properly placed
            # self.text = self.doc.toHtml()
        else:
            self.doc = QTextDocument()
            self.doc.setDocumentMargin(0) # important so that the square is properly placed

            textOption = self.doc.defaultTextOption()
            textOption.setWrapMode(QTextOption.NoWrap)
            self.doc.setDefaultTextOption(textOption)

            if text is not None:
                self.doc.setHtml(text)
                # self.setText(text)
            # else:
                # self.setText('')
            # self.text = text
        # self.isSet = True
        self.doc.adjustSize()
        size = self.getSize()

        super(TAText2D, self).__init__(x if x is not None else 0, y if y is not None else 0, size.width(), size.height())
        self.opacity = opacity
        self.immutable=True
        self.line_style = None # useless just for compat with other shapes
        if placement is not None:
            if not isinstance(placement, Position):
                placement = Position(placement)
        self.placement = placement
        self.fill_color = fill_color
        self.color = color
        self.text_orientation = text_orientation
        self.range = range # this will contain the spanning of text over several elements only used and useful for text rows
        self.__version = __version
        self.is_letter = is_letter
        # if x is not None:
        #     self.setX(x)
        # if y is not None:
        #     self.setY(y)

    def _layout_doc(self):
        """The document that is drawn and measured: self.doc with its $…$
        typeset as maths (batoolset.drawings.math_text), or self.doc itself.
        self.doc keeps the raw text: it is what is saved and edited."""
        # (cached in math_text, never on self: self is saved and copied)
        try:
            from batoolset.drawings.math_text import typeset_for
            return typeset_for(self, self.doc)
        except Exception:
            logger.error('could not typeset the maths in "' + self.doc.toPlainText() + '"')
            return self.doc

    def set_range(self, range):
        # this is the range of labels in text rows
        self.range = range

    def set_opacity(self, opacity):
        self.opacity = opacity

    def setText(self, html):
        self.doc.setHtml(html)
        # self.doc.adjustSize()
        # size = self.getSize()
        # self.setWidth(size.width())
        # self.setHeight(size.height())
        self.setDoc(self.doc)
        # self.text = html

    def setDoc(self, doc):
        self.doc = doc
        self.doc.setDocumentMargin(0)
        self.doc.adjustSize()
        size = self.getSize()
        self.setWidth(size.width())
        self.setHeight( size.height())
        # self.text = self.getHtmlText()

    def draw(self, painter, draw=True, parent=None):
        if draw:
            self.scale=1 # TODO FIX THIS BETTER TATEXT SHOULD NEVER BE RESCALED just a hack so that the scale is always preserved (importantly the square is properly positioned but the text is not (probably needs be cntered on the rect center) no big deal I guess
            # LaTeX "PDF+LaTeX" export renders the graphics with text suppressed so
            # the text can be typeset by LaTeX; the rect/size is left untouched so the
            # parent's placement is unaffected and the overlay coordinates stay correct
            if getattr(self, '_latex_hide', False):
                return
            painter.save()

            # transform = QTransform()
            # transform.rotate(0)  # Rotate 45 degrees clockwise
            # painter.setWorldTransform(transform)


            # Get the rotation angle of the transform
            # Get the current transformation and rotation

            # transform, rotation_angle = get_painter_transform_and_rotation(painter) # this is ok --> this is 0
            # print(f"Current transformation matrix: {transform}")
            # print(f"Current rotation angle: {rotation_angle:.2f} degrees")

            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.NoBrush)

            # Get the current clip rect of the painter
            # current_clip_rect = painter.clipBoundingRect()
            # print('current_clip_rect',current_clip_rect)

            # print('self.placement, self.placement.isEmpty()',self.placement, self.placement.isEmpty())

            rect_to_plot = self.getRect(scale=True)
            if self.placement is  None or self.placement.isEmpty():
            # if True:
                # painter.setClipRect(self.getRect(scale=True)) # in fact this is needed to get text to work!!! # DO NOT DO THIS OTHERWISE THE TEXT IS NOT CLIPPED WHICH IS NOT WHAT I WANT!!!!
                # if text --> need center v or h --> TODO
            # else:
                rect_to_plot = self.getRect(scale=True)

                if parent is not None and parent.scale is not None and parent.scale != 1:
                    rect_to_plot = QRectF(rect_to_plot.x() / parent.scale, rect_to_plot.y() / parent.scale, rect_to_plot.width() / parent.scale,rect_to_plot.height() / parent.scale)
                    # neo
                    # rect_to_plot = self.getRect(scale=True)
                    # rect_to_plot.setX(rect_to_plot.x()/parent.scale)
                    # rect_to_plot.setY(rect_to_plot.y()/parent.scale) # now this shit is huge
                    # somehow this is required for text but why ????

                # print('rect_to_plot', rect_to_plot)
                if parent is not None:
                    rect_to_plot = rect_to_plot.translated(parent.topLeft())
                # print('rect_to_plot2',rect_to_plot)

            #DEBUG
            if False:
                painter.setPen(QtCore.Qt.red)
                painter.drawRect(rect_to_plot)

            # do not move this, this is where the fill color should be applied
            if self.fill_color is not None:
                # if isinstance(self.fill_color, QColor):
                #     self.fill_color = self.fill_color.rgb() & 0xFFFFFF

                # print(self, self.fill_color, 'inside drawing')

                # somehow the rect pos is completely wrong

                # painter.setPen(QtCore.Qt.red)
                painter.setBrush(QBrush(QColor(self.fill_color)))
                painter.save()

                # all seems to be fixed now but allI do here is totally crazy -−> DO A CLEAN FIX OF THE STUFF SOME DAY
                rect2 =QRectF(rect_to_plot.x(), rect_to_plot.y(), rect_to_plot.width(), rect_to_plot.height())
                text_width = self._layout_doc().documentLayout().documentSize().width()
                text_height = self._layout_doc().documentLayout().documentSize().height()
                # very dirty fix I have to fix all more poperly some day this is totally abnormal that I have to do all of this !!! --< now that fixes the size but not the position --> somehow I am missing something still
                rect2.setWidth(text_width)
                rect2.setHeight(text_height)





                # this is not totally ok
                if self.text_orientation is not None and not 'X' in self.text_orientation:
                    # painter.translate(rect_to_plot.center())
                    # painter.rotate(90)
                    # painter.translate(-(rect_to_plot.center()))
                    # painter.translate(-)
                    painter.translate(rect_to_plot.topLeft())
                    painter.translate(rect_to_plot.height(), 0)
                    painter.rotate(get_angle(self.text_orientation))
                    painter.translate(-rect_to_plot.topLeft())  # presque -−> doit etre aligne au coin gaughe


                # else:
                painter.translate(rect_to_plot.center() - rect2.center())


                painter.drawRect(rect2)
                painter.restore()
                # self.doc.drawContents(painter)

                # this is positioned properly so why isn't text positioned there too!!! ???

            # self.doc.drawContents(painter)

            # if self.theta is not None and self.theta != 0:
            if self.theta is not None and self.theta != 0:
              # I have added support for rotation to that maybe I will need something smarter if rotation 90 degrees or flips and images no same width and height
              painter.translate(rect_to_plot.center())
              painter.rotate(self.theta)
              painter.translate(-rect_to_plot.center())

            if  self.text_orientation is not None and not 'X' in self.text_orientation: # self.text_orientation is not None: #  and not 'X' in self.text_orientation
                # very good -> that does the job --> the only thing is that of course it selection is not correct --> need fix it
                painter.translate(rect_to_plot.topLeft())
                painter.translate(rect_to_plot.height(), 0)
                painter.rotate(get_angle(self.text_orientation))
                painter.translate(-rect_to_plot.topLeft()) # presque -−> doit etre aligne au coin gaughe
                # painter.translate(rect_to_plot.height(),0) # presque -−> doit etre aligne au coin gaughe

            # self.doc.drawContents(painter)
            # if True: #TODO remove that debug only
            #     painter.drawRect(rect_to_plot)

            # if self.opacity is not None:
            # painter.setOpacity(self.opacity)

            # if False:
            painter.translate(rect_to_plot.x(), rect_to_plot.y())



            if False:
                text_width = self.doc.documentLayout().documentSize().width()
                text_height = self.doc.documentLayout().documentSize().height()
                # rect_of_doc = self.doc.documentRect()
                painter.setClipRect(QRectF(rect_to_plot.x(), rect_to_plot.y(),min(text_width, rect_to_plot.width()),min(text_height, rect_to_plot.height())))



            if True:
                text_width = self._layout_doc().documentLayout().documentSize().width()
                text_height = self._layout_doc().documentLayout().documentSize().height()
                # print('text_width, text_height',text_width, text_height, rect_to_plot, 'BINGO BINGO2')
                painter.translate((rect_to_plot.width()-text_width)/2, (rect_to_plot.height()-text_height)/2) # le bug est bien ici --> somehow the rect is still not correct and wrongly scaled --> what is the bug ?


                # with that the rect size is ok but the position is completely crap
                # if self.fill_color:
                #     text_width = self.doc.documentLayout().documentSize().width()
                #     text_height = self.doc.documentLayout().documentSize().height()
                #     # very dirty fix I have to fix all more poperly some day this is totally abnormal that I have to do all of this !!! --< now that fixes the size but not the position --> somehow I am missing something still
                #     rect_to_plot.setWidth(text_width)
                #     rect_to_plot.setHeight(text_height)
                #     painter.setBrush(QBrush(QColor(self.fill_color)))
                #     painter.drawRect(rect_to_plot)

            # painter.translate(self.x()+self.width()/2., self.y()+self.height()/2.) # if I do that the square and the

            # here I need a cliprect of just the size of the stuff and not even that but the intersection with the parent
            # painter.translate(-rect_to_plot.center())

            # shall I get the rect of the doc and see if it fits the other otherwise probably I need to center it at least I can check that


            # not 'X' in self.text_orientation
            if self.text_orientation and '-' in self.text_orientation:# self.text_orientation and '-' in self.text_orientation:
                painter.rotate(180) # ok but the pb is then I need to shift it back again
                painter.translate(-rect_to_plot.width(), -rect_to_plot.height())

            # painter.setWorldTransform(QTransform())
            #
            # transform, rotation_angle = get_painter_transform_and_rotation(painter) # this is ok --> this is 0
            # print(f"DEBUG Current transformation matrix: {transform}")
            # print(f"Current rotation angle: {rotation_angle:.2f} degrees")
            # print(self.text_orientation, '-->',get_angle(self.text_orientation)) # NO BUG IS THERE YET RANDOM ....
            # painter.resetTransform()
            self._layout_doc().drawContents(painter)








            painter.restore()
            # maybe activate this upon debug
            # painter.save()
            # painter.setPen(QtCore.Qt.red)
            # painter.drawRect(self)
            # painter.restore()

    # def set_to_scale(self, factor): # this object should not be rescalable
        # raise Exception('this should not be called --> this creates a bug because the size fo this object is immutable')
        # self.scale = 1

    def boundingRect(self): # is that ok also
        return self

    def getSize(self): # is that ok ???
        return self._layout_doc().size()

    def getWidth(self):
        return self.boundingRect().width()

    def getHeight(self):
        return self.boundingRect().height()

    def setText(self, text):
        self.doc.setHtml(text)
        # size = self.size()
        # self.setWidth(size.width(), size.height())
        self.setDoc(self.doc)

    # def sync_text(self): # TODO always make sure to call this whenever a change to the text is made -−> will ease the serialization
    #     self.text = self.getHtmlText()

    def getRect(self,*args, **kwargs):
        # print('self.scale of the text', self.scale)

        text_width = self._layout_doc().documentLayout().documentSize().width()
        text_height = self._layout_doc().documentLayout().documentSize().height()
        # if args:
        if args or kwargs:
            rect = QRectF(self.x()*self.scale, self.y()*self.scale, text_width, text_height)
            if self.text_orientation is not None and not 'X' in self.text_orientation and 'all' in kwargs:
                t = QTransform().translate(rect.x(), rect.y()).translate(rect.height(),0).rotate(90).translate(-rect.x(), -rect.y())
                rotatedPolygon = t.mapToPolygon(rect.toRect())  # Map the rectangle to a rotated polygon

                # Create a QRectF from the bounding rectangle of the rotated polygon
                rotatedRect = rotatedPolygon.boundingRect()
                rotatedRect = QRectF(rotatedRect.x(), rotatedRect.y(), rotatedRect.width(), rotatedRect.height())
                rect = rotatedRect
            return rect
        else:
            # if args or kwargs:
            return QRectF(self.x(), self.y(), text_width, text_height)

    def width(self, *args, **kwargs):
        return self.getRect(*args, **kwargs).width()

    def height(self, *args, **kwargs):
        return self.getRect(*args, **kwargs).height()

    # def getRect(self,*args, **kwargs):
    #     if args or kwargs:
    #         if 'all' in kwargs:
    #             # print('in there!')
    #             # rect_to_plot = QRectF(*super().getRect())#QRectF(self.x(), self.y(), self.width() / self.scale, self.height() / self.scale)
    #             rect_to_plot = QRectF(self.x(), self.y(), self.width() / self.scale, self.height() / self.scale)
    #             center = rect_to_plot.center()
    #             if self.theta:
    #                 # t = QTransform().translate(center.x(), center.y()).rotate(self.theta).translate(-center.x(),-center.y())
    #                 # rotatedRect = t.mapToPolygon(rect_to_plot.toRect())  # // mapRect() returns the bounding rect
    #                 t = QTransform().translate(center.x(), center.y()).rotate(self.theta).translate(-center.x(),
    #                                                                                                 -center.y())
    #                 rotatedPolygon = t.mapToPolygon(rect_to_plot.toRect())  # Map the rectangle to a rotated polygon
    #
    #                 # Create a QRectF from the bounding rectangle of the rotated polygon
    #                 rotatedRect = QRectF(rotatedPolygon.boundingRect())
    #             else:
    #                 return rect_to_plot
    #             try:
    #                 return QRectF(rotatedRect.boundingRect())
    #             except:
    #                 return rotatedRect
    #             # return QRectF(self.x(), self.y(), self.width() / self.scale, self.height() / self.scale)
    #         else:
    #             # default to scaled object
    #             return QRectF(self.x(), self.y(), self.width()/self.scale, self.height()/self.scale)

    # def __getstate__(self):
    #     # Return a dictionary containing the state of the object
    #     return {'text': self.getHtmlText()}
    #
    # def __setstate__(self, state):
    #     # Set the state of the object from the dictionary
    #     self.setText(state['text'])

    # shall I rather compute its size including the roitation so that it never gets truncated --> that does make sense -−> need compute the bounds of the rotated stuff
    # and the incompressible size should also depend on that

    # def getIncompressibleWidth(self):
    #     # TODO in fact take the rotated size --> much smarter here --> see how I can do
    #     return self.width()
    #
    # def getIncompressibleHeight(self):
    #     return self.height()
    #
    # def get_incompressible_size(self, axis=None):
    #     # if True:
    #     #     return self.width()
    #     # if self.theta is not None:
    #         # get width and or height
    #     if axis:
    #         if axis == 'X':
    #             return self.getIncompressibleWidth()
    #         else:
    #             return self.getIncompressibleHeight()

    def setTopLeft(self, *args):
        if args:
            # cur_top_left = self.topLeft()
            # print('cur_top_left', cur_top_left, args)
            if len(args)==1:
            #     # assume a QpointF
                self.moveTo(args[0].x(), args[0].y())
            elif len(args) == 2:
                self.moveTo(QPointF(args[0], args[1]))
            # self.update_bounds()
            # elif len(args)==2:
            #     for img in self.content:
            #         img.moveTopLeft(QPointF(args[0], args[1]))
            # else:
            #     # logger.error('invalid args for top left')
            #     print('invalid args for top left')


    # def set_P1(self, *args):
    #     if not args:
    #         logger.error("no coordinate set...")
    #         return
    #     if len(args) == 1:
    #         self.moveTo(args[0].x(), args[0].y())
    #     else:
    #         self.moveTo(QPointF(args[0], args[1]))
    #
    # def get_P1(self):
    #     return QPointF(self.x(), self.y())

    def getPlainText(self):
        return self.doc.toPlainText()

    def getHtmlText(self):
        return self.doc.toHtml()

    def __repr__(self):
        class_name = type(self).__name__
        memory_address = hex(id(self))
        return f"{class_name}-{memory_address}"

    def to_dict(self):
        x = self.x()
        y = self.y()
        # width = self.width()
        # height = self.height()

        # Create a dictionary representation of the values of the super object
        output_dict = {
            'x': x,
            'y': y,
            'text': self.getHtmlText(),

            # 'width': width,
            # 'height': height,
            # 'args':self.filename,
            # 'filename':self.filename,
        }

        # print(output_dict)
        # Update the dictionary with the __dict__ of Rectangle2D
        output_dict.update(self.__dict__) # not smart because overrides the outputdict

        output_dict['range']=self.range if self.range is None else str(self.range) # force convert it to text]


        return output_dict

if __name__ == '__main__':
    # this could be a pb ...
    app = QApplication(sys.argv)# IMPORTANT KEEP !!!!!!!!!!!

    # window = MyWidget()
    # window.show()

    # ça marche car ça override la couleur par defaut du truc
    # c'est parfait et 2000X plus facile que ds java --> cool

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

    # html = "<font color=blue size=24>this is a test<sup>2</sup><br></font><font color=green size=12>continued<sub>1</sub><br></font><font color=white size=12>test greek <font face='Symbol' size=32>a</font> another &alpha;<font face='Arial' color='Orange'>I am a sentence!</font>"
    text = TAText2D(html)

    # hexagon.append(QPointF(10, 20))
    print(text)

    # print(hexagon.translate(10, 20)) # why none ???
    # translate and so on can all be saved...

    image = QImage('/E/Sample_images/sample_images_PA/mini/focused_Series012/handCorrection.png')
    # image = QImage(QSize(400, 300), QImage.Format_RGB32)
    painter = QPainter()
    painter.begin(image)
    # painter.setOpacity(0.3);
    painter.drawImage(0, 0, image)
    painter.setPen(QtCore.Qt.blue)
    text.opacity = 0.7
    painter.translate(10, 20)
    painter.setPen(QColor(168, 34, 3))

    text.draw(painter) # ça marche pourrait overloader ça avec du svg

    painter.drawRect(text)# try to draw the bounds

    # painter.setPen(QtCore.Qt.green)
    # painter.setFont(QFont('SansSerif', 50))


    painter.setFont(QFont('Decorative', 10))
    painter.drawText(256, 256, "this is a test")

# nothing works it just doesn't draw for unknown reason ????
#     painter.drawText(QRect(60,60,256,256), Qt.AlignCenter, "this is a test")

    painter.setPen(QtGui.QColor(0, 255, 255)) # colors are weird !!!
    # painter.drawText(20, 20, "MetaGenerator") # fait planter le soft --> pkoi exit(139) ...
    painter.drawText(QRect(60,60,256,256), Qt.AlignCenter, "Text centerd in the drawing area")

    # painter.drawText(QRect(100, 100, 200, 100), "Text you want to draw...");
    print('here')
    painter.end()

    # image = QImage(QSize(400, 300), QImage::Format_RGB32);
    # QPainter
    # painter( & image);
    # painter.setBrush(QBrush(Qt::green));
    # painter.fillRect(QRectF(0, 0, 400, 300), Qt::green);
    # painter.fillRect(QRectF(100, 100, 200, 100), Qt::white);
    # painter.setPen(QPen(Qt::black));


    # painter.save()
    # painter.setCompositionMode(QtGui.QPainter.CompositionMode_Clear)
    # painter.eraseRect(r)
    # painter.restore()
    print('saving', '/E/trash//test_pyQT_draw_text.png')
    image.save('/E/trash/test_pyQT_draw_text.png', "PNG")


    # split text and find bounding rect of the stuff --> so that it is well positioned
    # or do everything in svg and just show what's needed ???

    #pas mal TODO faire une classe drawsmthg qui dessine n'importe quelle forme que l'on lui passe avec des parametres de couleur, transparence, ...

    # tt marche aps mal ça va très vite
    sys.exit(0)
