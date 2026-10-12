# Here I will store all the GUI parameters (such as Y spacing) so that I can restore them too


class SerializableGUIparameters():
    # min = None, max = None,
    def __init__(self, space=3, background=None, **kwargs):
        self.space = space
        # figure-wide background colour (0xRRGGBB) behind panels and gaps; None = none
        self.background = background
        # see what are the other things I can store
