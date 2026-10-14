# Here I will store all the GUI parameters (such as Y spacing) so that I can restore them too


class SerializableGUIparameters():
    # min = None, max = None,
    def __init__(self, space=3, background=None, first_letter=None, auto_lettering=None, **kwargs):
        self.space = space
        # figure-wide background colour (0xRRGGBB) behind panels and gaps; None = none
        self.background = background
        # panel lettering: the first letter ('A' or 'a'...) and whether panels are
        # lettered at all; None in files saved before they were stored
        self.first_letter = first_letter
        self.auto_lettering = auto_lettering
        # see what are the other things I can store
