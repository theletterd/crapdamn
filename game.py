import curses
from curses import wrapper
stdscr = curses.initscr()
import time
import sprites
#import random


FRAMERATE = 30
SLEEPTIME = 1.0 / FRAMERATE

class Drawable(object):
    is_killed = False

    def __init__(self, y, x):
        self.y = y
        self.x = x

    def sprite(self):
        return "NaS"

    def draw(self, stdscr):
        if self.is_killed:
            pass

        split_sprite = [line for line in self.sprite().split('\n') if line]
        # we might need to define a valid box at some point
        for index, line in enumerate(split_sprite):
            stdscr.addstr(self.y + index, self.x, line)

    def is_live(self):
        return not self.is_killed

    def tick(self):
        pass

    def kill(self):
        self.is_killed = True


class Collidable(Drawable):
    def health():
        pass

    def collision_coords(self):
        # yield a list of y, x tuples
        split_sprite = [line for line in self.sprite().split('\n') if line]

        for y_index, line in enumerate(split_sprite):
            for x_index, character in enumerate(line):
                if not character.isspace():
                    yield(self.y + y_index, self.x + x_index)

    def register_damage(self):
        pass


class Ship(Collidable):

    def sprite(self):
        return sprites.ship

    def constrain(self):
        if self.x < 0:
            self.x = 0

        if self.y < 0:
            self.y = 0

    def nose_coords(self):
        return [self.y - 1, self.x + 1]


class Curse(Collidable):

    def __init__(self, curse, y, x):
        self.base_word = curse.upper()
        self.curse = self._cursify(self.base_word)
        super(Curse, self).__init__(y, x)

    def _cursify(self, word):
        top_line = "| " + word + " |"
        bottom_line = "\{}/".format(('-' * (len(word) + 2)))
        return top_line + '\n' + bottom_line

    def sprite(self):
        return self.curse

    def draw(self, stdscr):
        if self.is_killed:
            pass

        # we know that with the curse. there's only two lines.
        split_sprite = [line for line in self.sprite().split('\n') if line]

        line_0 = split_sprite[0]
        line_1 = split_sprite[1]

        # choose color based on percent damage...
        num_asterisks = len([char for char in self.base_word if char != '*'])
        damage = num_asterisks / float(len(self.base_word))
        color = curses.color_pair(1)
        if damage < 0.66:
            color = curses.color_pair(2)
        if damage < 0.33:
            color = curses.color_pair(3)

        stdscr.addstr(self.y, self.x, line_0, color)
        stdscr.addstr(self.y + 1, self.x, line_1, curses.color_pair(4))

        # re-draw the first/last character of line_0
        stdscr.addstr(self.y, self.x, line_0[0], curses.color_pair(4))
        stdscr.addstr(self.y, self.x + len(line_0) -1, line_0[-1], curses.color_pair(4))

    def register_damage(self):
        remaining_indices = [index for index, character in enumerate(self.base_word) if character is not '*']
        if not remaining_indices:
            self.kill()
        else:
            # random looks kind of shitty
            #choice = random.choice(remaining_indices)
            choice = remaining_indices[0]
            self.base_word = self.base_word[:choice] + '*' + self.base_word[choice + 1:]
            self.curse = self._cursify(self.base_word)

class Bullet(Drawable):

    def sprite(self):
        return '*'

    def tick(self):
        self.y -= 1

    def is_live(self):
        # check to see if we fly off the top of the screen, then remove
        return self.y >= 0 and (not self.is_killed)

class ShipBullet(Bullet):

    def sprite(self):
        return sprites.bullet

def log(message):
    stdscr.addstr(0, 0, message)

def init_colors():
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

def game(stdscr):
    stdscr.nodelay(1)
    curses.curs_set(0)
    curses.start_color()
    init_colors()

    # TODO get the window size
    ship = Ship(30,50)
    drawable_elements = []
    drawable_elements.append(ship)
    drawable_elements.append(Curse("mothertrucker", 4, 20))
    drawable_elements.append(Curse("crap", 6, 10))
    drawable_elements.append(Curse("damn", 10, 24))
    drawable_elements.append(Curse("butts", 7, 28))
    drawable_elements.append(Curse("dillhole", 3, 5))

    while True:
        stdscr.clear()
        drawable_elements = [element for element in drawable_elements if element.is_live()]

        # define collision map
        collidable_elements = [element for element in drawable_elements if isinstance(element, Collidable)]
        collidable_map = {}
        for element in collidable_elements:
            for coord in element.collision_coords():
                collidable_map[coord] = element

        # check for collision
        #bullets = [element for element in drawable_elements if type(element) ==  Bullet]
        bullets = [element for element in drawable_elements if isinstance(element, Bullet)]
        log(str(len(bullets)))
        for bullet in bullets:
            if (bullet.y, bullet.x) in collidable_map:
                collidable_map[(bullet.y, bullet.x)].register_damage()
                bullet.kill()

        # go through
        for element in drawable_elements:
            element.draw(stdscr)
            if type(element) is Ship:
                ship.constrain()

            element.tick()

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            ship.x -=1
        elif key == curses.KEY_RIGHT:
            ship.x +=1
        elif key == curses.KEY_UP:
            ship.y -=1
        elif key == curses.KEY_DOWN:
            ship.y +=1
        elif key == ord(' '):
            drawable_elements.append(ShipBullet(*ship.nose_coords()))

        time.sleep(SLEEPTIME)

wrapper(game)
