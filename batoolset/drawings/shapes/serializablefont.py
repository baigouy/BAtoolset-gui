from batoolset.drawings.shapes.Position import Position
from batoolset.drawings.shapes.txt2d import TAText2D
from batoolset.pyqts.tools import get_html_text_with_font
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from qtpy.QtGui import QFont
from qtpy.QtWidgets import QApplication
# from qtpy.QtCore import Qt
import sys

class SerializableQFont(QFont):

    def __init__(self, *args, **kwargs):
        # print('kwargs of qfont', kwargs)
        # print('args of qfont', args)

        self.foreground = 0x000000
        if 'foreground' in kwargs:
            self.foreground = kwargs['foreground']
            del kwargs['foreground']

        self.background = 0xFFFFFF
        if 'background' in kwargs:
            self.background = kwargs['background']
            del kwargs['background']
        self.placement = Position('top-left')
        if 'placement' in kwargs:
            if isinstance(kwargs['placement'], Position):
                self.placement = kwargs['placement']
            else:
                self.placement = Position(kwargs['placement'])
            del kwargs['placement']


        super().__init__(*args, **kwargs)


        # print('kwargs of qfont', kwargs)
        # print('args of qfont', args)

        # tmp_font = None
        # if args:
        #     if isinstance(args[0], SerializableQFont):
        #         print('BINGO', args[0].foreground, args[0].background)
        #     else:
        #         print('PAS BINGO', type(args[0]))




    def to_dict(self):
        """Convert the SerializableQFont object to a dictionary."""
        return {
            'family': self.family(),
            'size': max(self.pointSize(),1), # just in case pointsize is 0
            'style': self.weight(), # if self.weight() == QFont.Normal else 'Bold'
            'italic': self.italic(),
            'background': self.background,
            'foreground': self.foreground,
            'placement':self.placement.position_to_string(),
        }

    @staticmethod
    def from_dict(font_dict):
        """Create a SerializableQFont object from a dictionary."""
        font = SerializableQFont(font_dict.get('family', 'Arial'), pointSize=font_dict.get('size', 12), weight=font_dict.get('style', QFont.Normal), italic=font_dict.get('italic', False), background = font_dict.get('background', None),foreground = font_dict.get('foreground', None), placement=Position(font_dict.get('placement', 'top-left')))
        return font

    def format_text_with_font(self, text):
        return get_html_text_with_font(text, self)


    # self.foreground
    def get_letter_html(self, text, foreground=None):
        """*foreground* (0xRRGGBB int) overrides the font colour for this letter,
        e.g. dark letters on a white chart panel when the figure uses white."""
        fg = self.foreground if foreground is None else foreground
        if fg is not None:
            text = f'<font color=#{fg:06x}>{text}</font>'
        return self.format_text_with_font(text)

    def get_TaText2D_with_font(self, text, foreground=None):
        return TAText2D(self.get_letter_html(text, foreground=foreground), placement=self.placement,
                        fill_color=self.background, is_letter=True)

    def __copy__(self):
        return self

    def __deepcopy__(self, memo):
        return self

        # be careful with that because this is what is compared when using == !!! so if poorly implemented this can have dramatic effects

    def __str__(self):
        #     return f"{ self.__class__.__name__} {self.ID}"
        return self.__repr__()
        #
        # def __repr__(self):
        #     return self.__str__()

    def __repr__(self):
        class_name = type(self).__name__
        memory_address = hex(id(self))
        return f"{class_name}-{memory_address}"

def main():
    # Create a SerializableQFont object
    font = SerializableQFont()
    font.setFamily('Arial')
    font.setFamily('Comic Sans MS')
    font.setPointSize(12)
    font.setWeight(QFont.Normal)
    font.setItalic(True)
    font.background = 0xFF0000
    font.foreground = 0x0000FF

    # Convert the SerializableQFont object to a dictionary
    font_dict = font.to_dict()
    print(font_dict)

    # Convert the SerializableQFont object to a JSON string
    # Create a SerializableQFont object from a dictionary
    font2 = SerializableQFont.from_dict(font_dict)
    print(font2.family(), font2.pointSize(), font2.weight(), font2.italic())

    # Exit the QApplication


if __name__ == '__main__':
    # Initialize the QApplication
    app = QApplication(sys.argv)
    main()
    # sys.exit(app.exec_())