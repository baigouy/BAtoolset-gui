# TODO make these things combined with pack and align commands and make loops
# this way I can make any component at any specific position !!!
# this is quite good I think
import copy
import traceback
from itertools import groupby


from batoolset.figure.alignment import packing_modes


# Define a sorting key function to sort objects based on their positions
def sorting_key(obj):
    try:
        return tuple(sorted(obj.items()))
    except Exception:
        try:
            return tuple(sorted(obj.placement.get_position()))
        except Exception:
            # pass
            return ('free','relative') # if the object does not have a position assume it obeys free/relative positioning

def groupby_position(objects):
    from batoolset.drawings.shapes.txt2d import TAText2D
    if isinstance(objects, TAText2D):
        objects = [objects]
    # Sort the objects based on their positions
    sorted_objects = sorted(objects, key=sorting_key)
    # Group the sorted objects based on their positions
    grouped_objects = {key: list(group) for key, group in groupby(sorted_objects, key=sorting_key)}
    return grouped_objects


class Position:
    positions = {
        'top': False,
        'bottom': False,
        'left': False,
        'right': False,
        'center_h': False,
        'center_v': False
    }

    def __init__(self, position=None):
        self.positions = copy.deepcopy(Position.positions)
        if position is not None:
            self.set_position(position)

    def set_position(self, position):
        for key in self.positions.keys(): # reset all positions
            self.positions[key] = False

        if not position:
            return

        position = position.lower()
        # except:
        #     traceback.print_exc()
        #     print('position', position)

        if 'top' in position:
            self.positions['top'] = True
        if 'bottom' in position:
            self.positions['bottom'] = True
        if 'left' in position:
            self.positions['left'] = True
        if 'right' in position:
            self.positions['right'] = True
        if 'center_h' in position:
            self.positions['center_h'] = True
        if 'center_v' in position:
            self.positions['center_v'] = True

    def get_position(self):
        return {key: value for key, value in self.positions.items() if value}

    def check_position(self, position):
        if not position in self.positions:
            return False
        return self.positions[position]

    def position_to_string(self):
        out = ''
        if self.positions['top']:
            out += 'top '
        if self.positions['bottom']:
            out += 'bottom '
        if self.positions['left']:
            out += 'left '
        if self.positions['right']:
            out += 'right '
        if self.positions['center_h']:
            out += 'center_h '
        if self.positions['center_v']:
            out += 'center_v '

        return out.strip()

    def get_packing_orientation(self):
        # try rescue packing mode from position
        # if reference.position.get_position():
        if self.check_position('top'):
            return packing_modes[1]
        elif self.check_position('bottom'):
            return packing_modes[3]
        # elif mode.check_position('left'):
        #     mode = packing_modes[0]
        # elif mode.check_position('right'):
        #     mode = packing_modes[2]
        # else:
        #     # logger.error('unknown positioning --> ignoring')
        #     print('unknown position ignoring')

    def isEmpty(self):
        for key, value in self.positions.items():
            if value:
                return False
        return True

    def __str__(self):
        return self.position_to_string()

# very good --> maybe just slightly improve it and fix it --> it will be placed with repsect to the parent stuff
if __name__ == '__main__':
    # Create a new Position object
    p = Position()
    print(p.get_position()) # --> empty

    # Set the position
    p.set_position('top left')
    # Get the current position
    print(p.get_position())  # Output: {'top': True, 'left': True}

    p.set_position('TOp Left')
    # Get the current position
    print(p.get_position())  # Output: {'top': True, 'left': True}

    p.set_position('Bottom Right')
    # Get the current position
    print(p.get_position())  # Output: {'top': True, 'left': True}


    print('pos to string', p.position_to_string())

    print(p.check_position('top'))
    print(p.check_position('right'))
    print(p.check_position('bottom'))

    p2 = Position()



    print(p2.get_position())

    print(p2.isEmpty())
    print(p.isEmpty())



    if False:

        # List of objects with positions
        objects = [
            {'top': True, 'left': True},
            {'bottom': True, 'right': True},
            {'top': True, 'left': True},
            {'bottom': True, 'left': True}
        ]

        grouped_objects = groupby_position(objects)




        print(grouped_objects)

        # Print the grouped objects
        for position, objects_in_group in grouped_objects.items():
            print(f"Position: {position}")
            for obj in objects_in_group:
                print(obj)
            print()

