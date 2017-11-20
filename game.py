import curses
import constants

stdscr = curses.initscr()
stdscr.nodelay(1)
curses.start_color()
stdscr.clear()


from curses import wrapper
import time
import random



from drawables import BackgroundStar
from drawables import CurseBullet
from drawables import ShipBullet
from drawables import Bullet
from drawables import Collidable
from drawables import Curse
from drawables import Ship


def log(message):
    stdscr.addstr(0, 0, message)


def game(stdscr):
    game_window = curses.newwin(constants.HEIGHT, constants.WIDTH, 0, 0)
    game_window.nodelay(1)

    # TODO get the window size
    ship = Ship(constants.HEIGHT - 10, constants.WIDTH / 2)
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

    background_elements = []
    for y in xrange(1, constants.HEIGHT - 2):
        for x in xrange(1, constants.WIDTH - 2):
            if random.random() <= constants.STAR_CHANCE:
                background_elements.append(BackgroundStar(y, x))

    while True:
        game_window.clear()
        game_window.border()
        for element in background_elements:
            element.draw(game_window)
            element.tick()

        drawable_elements = [element for element in drawable_elements if element.is_live()]

        # define collision map
        collidable_elements = [element for element in drawable_elements if isinstance(element, Collidable)]
        collidable_map = {}
        for element in collidable_elements:
            for coord in element.collision_coords():
                collidable_map[coord] = element

        # check for collision
        bullets = [element for element in drawable_elements if isinstance(element, Bullet)]
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
            element.draw(game_window)
            element.tick()

        game_window.refresh()
        key = stdscr.getch()

        if key in ship.move_keys:
            ship.move(key)

        elif key == ord(' '):
            bullet = ship.fire()

            if bullet:
                drawable_elements.append(bullet)

        curseships = [element for element in drawable_elements if type(element) == Curse]
        for curse in curseships:
            if random.random() < 0.01:
                drawable_elements.append(CurseBullet(*curse.get_gun_coords()))

        time.sleep(constants.SLEEPTIME)

wrapper(game)
