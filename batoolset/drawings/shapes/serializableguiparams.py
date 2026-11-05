# Here I will store all the GUI parameters (such as Y spacing) so that I can restore them too


class SerializableGUIparameters():
    # min = None, max = None,
    def __init__(self, space=3, background=None, first_letter=None, auto_lettering=None,
                 letter_layout=None, row_letter_align=None, **kwargs):
        self.space = space
        # figure-wide background colour (0xRRGGBB) behind panels and gaps; None = none
        self.background = background
        # panel lettering: the first letter ('A' or 'a'...) and whether panels are
        # lettered at all; None in files saved before they were stored
        self.first_letter = first_letter
        self.auto_lettering = auto_lettering
        # where the letters go: 'panel' (one in each panel, the default) or 'row'
        # (one per row, outside it on the left), and for 'row' whether the letter
        # is level with the 'top' or the 'center' of its row. Only kept when set,
        # so figures lettered per panel are saved exactly as before.
        if letter_layout is not None:
            self.letter_layout = letter_layout
        if row_letter_align is not None:
            self.row_letter_align = row_letter_align
        # see what are the other things I can store
