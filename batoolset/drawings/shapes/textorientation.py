def get_angle(text, verbose=False):
    if not text:
        # raise ValueError("Invalid orientation text: {}".format(self.text))
        if verbose:
            print(f'unknown text orientation {text}, assuming horizontal')
        return 0
    # angle =0
    if 'h' in text.lower() or 'x' in text.lower():
        angle = 0
    elif 'v' in text.lower() or 'y' in text.lower():
        angle = 90
    else:
        # raise ValueError("Invalid orientation text: {}".format(self.text))
        if verbose:
            print(f'unknown text orientation {text}, assuming horizontal')
        angle =0
    # if '-' in text:
    #     angle=-angle
    return angle


class TextOrientation:
    def __init__(self, text):
        self.text = text

    def get_angle(self, verbose=False):
        return get_angle(self.text, verbose=verbose)



if __name__ == '__main__':
    orientation = TextOrientation('horizontal')
    angle = orientation.get_angle()
    print(angle)  # Output: 0

    orientation = TextOrientation('Vertical')
    angle = orientation.get_angle()
    print(angle)  # Output: 90

    orientation = TextOrientation(None)
    angle = orientation.get_angle(verbose=TextOrientation)  # Raises ValueError
    print(angle)


    print(get_angle('-y'))