import sprites
import curses
import random
import colors
import constants


class Drawable(object):
    is_killed = False
    base_color = colors.WHITE

    def __init__(self, y, x):
        self._y = y
        self._x = x

    @property
    def x(self):
        return int(self._x)

    @property
    def y(self):
        return int(self._y)

    @property
    def width(self):
        return max(len(line) for line in self.sprite().split())

    @property
    def height(self):
        return len([line for line in self.sprite().split('\n') if line])

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

class BackgroundStar(Drawable):

    base_color = colors.WHITE


    def __init__(self, y, x):
        self._y = y
        self._x = x
        self.speed = random.choice([
            constants.STAR_SPEED_SLOW,
            constants.STAR_SPEED_FAST
        ])

        if self.speed == constants.STAR_SPEED_SLOW:
            self.base_color |= curses.A_DIM

    def sprite(self):
        return '.'

    def tick(self):
        self._y += self.speed
        if self.y > constants.HEIGHT - 2:
            # let's not kill stars - let's just put them back at the top
            self._y = 1

    def ship_moved(self, direction):

        if self.speed == constants.STAR_SPEED_SLOW:
            direction_speed = 0.2
        else:
            direction_speed = 0.6



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

    happy_color = colors.WHITE
    damage_color = colors.RED
    base_color = happy_color

    color_ticks = 3
    remaining_color_ticks = 0

    move_keys = set([
        curses.KEY_LEFT,
        curses.KEY_RIGHT,
        curses.KEY_UP,
        curses.KEY_DOWN,
    ])
    start_health = 10
    current_health = start_health
    current_sprite = sprites.ship
    dwell_ticks = 4
    remaining_dwell = 0

    max_bullets = 5
    bullets = max_bullets

    @property
    def height(self):
        # +2 for the health bar
        return super(Ship, self).height + 2

    def sprite(self):
        return self.current_sprite

    def constrain(self):
        if self.x < 1:
            self._x = 1

        if self.x + self.width >= constants.WIDTH - 1:
            self._x = constants.WIDTH - self.width - 1

        if self.y < 1:
            self._y = 1

        if self.y + self.height >= constants.HEIGHT - 1:
            self._y = constants.HEIGHT - self.height - 1


    def nose_coords(self):
        nose_index = len(self.sprite().split('\n')[1])
        return (self.y - 1, self.x + nose_index - 1)

    def register_damage(self):
        self.current_health -= 1
        self.base_color = self.damage_color
        if self.current_health < 0:
            self.kill()

    def tick(self):
        if self.remaining_dwell > 0:
            self.remaining_dwell -= 1
        else:
            self.current_sprite = sprites.ship

        if self.remaining_color_ticks > 0:
            self.remaining_color_ticks -= 1
        else:
            self.base_color = self.happy_color

        # also constrain here
        self.constrain()

        self.bullets += constants.BULLET_REFRESH
        if self.bullets > self.max_bullets:
            self.bullets = self.max_bullets

    def draw(self, stdscr):
        if self.is_killed:
            pass

        health_fraction = self.current_health / float(self.start_health)
        ship_color = self.base_color

        if health_fraction >= 0.75:
            health_color = colors.GREEN
        if health_fraction < 0.75:
            health_color = colors.YELLOW
        if health_fraction < 0.3:
            health_color = colors.RED
            ship_color |= curses.A_DIM

        split_sprite = [line for line in self.sprite().split('\n') if line]

        for index, line in enumerate(split_sprite):
            stdscr.addstr(self.y + index, self.x, line, ship_color)

        # jk, let's overwrite that last line in blue
        stdscr.addstr(self.y + len(split_sprite) -1, self.x, split_sprite[-1], colors.BLUE)


        # let's also add a gun meter
        gun_meter = "." * int((self.width * (self.bullets / float(self.max_bullets))))
        stdscr.addstr(self.y + len(split_sprite), self.x, gun_meter, colors.RED | curses.A_BOLD)

        # and a health-meter
        health_meter_length = self.width # max(len(line) for line in split_sprite)
        health_string_length = health_meter_length - 2
        num_health_characters = int(((self.current_health) / float(self.start_health)) * health_string_length)

        health_string = ('-' * num_health_characters) + (' ' * (health_string_length - num_health_characters))

        stdscr.addstr(self.y + len(split_sprite) + 1, self.x, '<' + (' ' * len(health_string)) + '>', health_color)
        stdscr.addstr(self.y + len(split_sprite) + 1, self.x + 1, health_string, health_color | curses.A_DIM)


    def move(self, key):
        if key == curses.KEY_LEFT:
            self._x -= constants.SHIP_SPEED
            self.current_sprite = sprites.ship_moving_left
        elif key == curses.KEY_RIGHT:
            self._x +=  constants.SHIP_SPEED
            self.current_sprite = sprites.ship_moving_right
        elif key == curses.KEY_UP:
            self._y -= 1
            self.current_sprite = sprites.ship_moving_up
        elif key == curses.KEY_DOWN:
            self._y += 1
            self.current_sprite = sprites.ship_moving_down

        if key in self.move_keys:
            self.remaining_dwell = self.dwell_ticks

        self.constrain()


    def fire(self):
        if self.bullets >= 1:
            self.bullets -= 1
            return ShipBullet(*self.nose_coords())

class Curse(Collidable):

    def __init__(self, curse, y, x):
        self.base_word = curse.upper()
        self.curse = self._cursify(self.base_word)
        self.direction = random.choice(['L', 'R'])
        self.speed = 0.5 # random.choice([1, 0.75, 0.6, 0.5, 0.33, 0.2, 0.1])
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

        if self.x < 1:
            self._x = 1
            self.direction = 'R'
            self._y += 1
            self.speed += 0.05

        if self.x + self.width  >= constants.WIDTH - 1:
            self._x = constants.WIDTH - self.width - 1
            self.direction = 'L'
            self._y += 1
            self.speed += 0.05

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
        color = colors.GREEN
        if damage < 0.66:
            color = colors.YELLOW
        if damage < 0.33:
            color = colors.RED

        shield_color = colors.MAGENTA
        stdscr.addstr(int(self.y), int(self.x), line_0, color)
        stdscr.addstr(int(self.y) + 1, int(self.x), line_1, shield_color)

        # re-draw the first/last character of line_0
        stdscr.addstr(int(self.y), int(self.x), line_0[0], shield_color)
        stdscr.addstr(int(self.y), int(self.x) + len(line_0) -1, line_0[-1], shield_color)

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
    base_color = colors.RED | curses.A_BOLD

    def is_live(self):
        # check to see if we fly off the top of the screen, then remove
        return self.y >= 1 and (not self.is_killed)

class CurseBullet(Bullet):

    frames = [
        sprites.curse_bullet_1,
        sprites.curse_bullet_2
    ]
    base_color = colors.CYAN | curses.A_BOLD

    def tick(self):
        self._y += 0.2

    def is_live(self):
        # check to see if we fly off the bottom of the screen, then remove
        return self.y <= (constants.HEIGHT - 2) and (not self.is_killed)


class StatusBar(Drawable):

    base_color = colors.WHITE | curses.A_BOLD

    def __init__(self, game_state):
        # status bar is in a fixed position always
        self._y = 1
        self._x = 1
        self.game_state = game_state

    @property
    def width(self):
        return constants.WIDTH - 2

    @property
    def height(self):
        return constants.HEIGHT - 2


    def draw(self, stdscr):
        score = str(self.game_state.score).rjust(8, '0') # gamestatus.score
        lives = self.game_state.remaining_lives
        message = self.game_state.message

        max_line_length = constants.WIDTH - 2
        line_start = "LIVES: {lives} ".format(lives=lives)
        line_middle = message
        line_end = " {score}".format(score=score)

        remaining_space = max_line_length - len(line_start) - len(line_end) - len(line_middle)
        padding = " " * (remaining_space / 2)
        line_middle = padding + line_middle + padding
        if remaining_space % 2:
            line_middle += " "

        line = line_start + line_middle + line_end

        #line = "LIVES: {lives}         {message}             {score}".format(score=score, lives=lives, message=message)
        stdscr.addstr(self.y, self.x, line, self.base_color)
