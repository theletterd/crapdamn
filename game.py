import curses
from curses import wrapper
stdscr = curses.initscr()
import time
import sprites
import random


FRAMERATE = 30
SLEEPTIME = 1.0 / FRAMERATE
SHIP_SPEED = 3

curses.curs_set(0)
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)


class Drawable(object):
    is_killed = False
    base_color = curses.color_pair(7)

    def __init__(self, y, x):
        self._y = y
        self._x = x

    @property
    def x(self):
        return int(self._x)

    @property
    def y(self):
        return int(self._y)

    def sprite(self):
        return "NaS"

    def draw(self, stdscr):
        if self.is_killed:
            pass

        split_sprite = [line for line in self.sprite().split('\n') if line]
        # we might need to define a valid box at some point
        for index, line in enumerate(split_sprite):
            stdscr.addstr(self.y + index, self.x, line, self.base_color)

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

    health = 10

    def sprite(self):
        return sprites.ship

    def constrain(self):
        if self.x < 0:
            self.x = 0

        if self.y < 0:
            self.y = 0

    def nose_coords(self):
        return (self.y - 1, self.x + 3)

    def register_damage(self):
        self.health -= 1
        if self.health < 0:
            self.kill()


class Curse(Collidable):

    def __init__(self, curse, y, x):
        self.base_word = curse.upper()
        self.curse = self._cursify(self.base_word)
        self.direction = random.choice(['L', 'R'])
        self.speed = random.choice([1, 0.75, 0.6, 0.5, 0.33, 0.2, 0.1])
        super(Curse, self).__init__(y, x)

    def _cursify(self, word):
        top_line = "| " + word + " |"
        bottom_line = "\{}/".format(('-' * (len(word) + 2)))
        return top_line + '\n' + bottom_line

    def tick(self):
        if self.direction == 'L':
            self._x -= self.speed
        elif self.direction == 'R':
            self._x += self.speed

        if self.x < 0:
            self._x = 0
            self.direction = 'R'

        if self.x >= 60:
            self._x = 60
            self.direction = 'L'

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

        stdscr.addstr(int(self.y), int(self.x), line_0, color)
        stdscr.addstr(int(self.y) + 1, int(self.x), line_1, curses.color_pair(4))

        # re-draw the first/last character of line_0
        stdscr.addstr(int(self.y), int(self.x), line_0[0], curses.color_pair(4))
        stdscr.addstr(int(self.y), int(self.x) + len(line_0) -1, line_0[-1], curses.color_pair(4))

    def register_damage(self):
        remaining_indices = [index for index, character in enumerate(self.base_word) if character is not '*']
        if not remaining_indices:
            self.kill()
        else:
            choice = remaining_indices[0]
            self.base_word = self.base_word[:choice] + '*' + self.base_word[choice + 1:]
            self.curse = self._cursify(self.base_word)

    def get_gun_coords(self):
        return (self.y + 2, self.x + int((len(self.base_word) + 2) / 2))



class Bullet(Drawable):

    sprite_generator = None
    frames = []

    def frame_generator(self):
        while True:
            for frame in self.frames:
                yield frame

    def sprite(self):
        if not self.sprite_generator:
            self.sprite_generator = self.frame_generator()

        return self.sprite_generator.next()

    def tick(self):
        self._y -= 1

    def is_live(self):
        pass

class ShipBullet(Bullet):

    frames = [
        sprites.ship_bullet_1,
        sprites.ship_bullet_2,
    ]
    base_color = curses.color_pair(5)

    def is_live(self):
        # check to see if we fly off the top of the screen, then remove
        return self.y >= 0 and (not self.is_killed)

class CurseBullet(Bullet):

    frames = [
        sprites.curse_bullet_1,
        sprites.curse_bullet_2
    ]
    base_color = curses.color_pair(6)

    def tick(self):
        self._y += 0.2

    def is_live(self):
        # check to see if we fly off the bottom of the screen, then remove
        return self.y <= 40 and (not self.is_killed)



def log(message):
    stdscr.addstr(0, 0, message)


def game(stdscr):
    stdscr.nodelay(1)

    # TODO get the window size
    ship = Ship(40,25)
    drawable_elements = []
    drawable_elements.append(ship)
    drawable_elements.append(Curse("dillhole", 3, 5))
    drawable_elements.append(Curse("mothertrucker", 6, 20))
    drawable_elements.append(Curse("crap", 9, 10))
    drawable_elements.append(Curse("butts", 12, 28))
    drawable_elements.append(Curse("nuts", 15, 24))
    drawable_elements.append(Curse("juicebox", 18, 3))
    drawable_elements.append(Curse("baghandler", 21, 15))
    drawable_elements.append(Curse("donkey", 24, 24))

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
        bullets = [element for element in drawable_elements if isinstance(element, Bullet)]
        log(str(len(drawable_elements)))
        for bullet in bullets:
            if (bullet.y, bullet.x) in collidable_map:
                collidable = collidable_map[(bullet.y, bullet.x)]

                # verify which bullets can damage which things
                if (((type(bullet) is ShipBullet) and (type(collidable) is Curse)) or
                    ((type(bullet) is CurseBullet) and (type(collidable) is Ship))):

                    collidable_map[(bullet.y, bullet.x)].register_damage()
                    bullet.kill()

        # go through and draw all elements
        for element in drawable_elements:
            element.draw(stdscr)
            if type(element) is Ship:
                ship.constrain()

            element.tick()

        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            ship._x -= SHIP_SPEED
        elif key == curses.KEY_RIGHT:
            ship._x +=  SHIP_SPEED
        elif key == curses.KEY_UP:
            ship._y -= 1
        elif key == curses.KEY_DOWN:
            ship._y += 1
        elif key == ord(' '):
            drawable_elements.append(ShipBullet(*ship.nose_coords()))

        curseships = [element for element in drawable_elements if type(element) == Curse]
        for curse in curseships:
            if random.random() < 0.01:
                drawable_elements.append(CurseBullet(*curse.get_gun_coords()))

        time.sleep(SLEEPTIME)

wrapper(game)
