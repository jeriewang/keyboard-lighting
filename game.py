from keyboard import *
from itertools import chain
from time import sleep, time
import numpy as np
import random
import curses
from normal import normal


def render(): keyboard.fx.advanced.draw()


class Counter:
    SEGMENTS = {
        1: SyncGroup(NUM_LK, NUM_SLASH, NUM_ASTERISK),
        2: SyncGroup(*get_keys('74'), NUM_LK),
        3: SyncGroup(*get_keys('96'), NUM_ASTERISK),
        4: SyncGroup(*get_keys('456')),
        5: SyncGroup(*get_keys('410')),
        6: SyncGroup(*get_keys('63'), NUM_DEL),
        7: SyncGroup(NUM_0, NUM_DEL)
    }

    # Using the 7-segment display model.
    # 1  1  1
    # 2     3
    # 2     3
    # 2     3
    # 4  4  4
    # 5     6
    # 5     6
    # 5     6
    # 7  7  7

    TENS = {
        1: PRT_SC,
        2: SCR_LK,
        3: PAUSE,
        4: INSERT,
        5: HOME,
        6: PAGE_UP,
        7: DEL,
        8: END,
        9: PAGE_DOWN
    }

    @classmethod
    def get_segments(cls, s: str):
        return tuple(map(lambda n: cls.SEGMENTS[int(n)], s))

    def __init__(self, bg: Color, fg: Color):
        self.keys = SyncGroup(*get_keys('1234567890'), NUM_LK, NUM_SLASH, NUM_ASTERISK, NUM_PLUS, NUM_ENTER, NUM_DEL,
                              PRT_SC, SCR_LK, PAUSE, INSERT, HOME, PAGE_UP, DEL, END, PAGE_DOWN)
        self.bg = bg
        self.fg = fg

    def reset(self):
        self.keys.set(self.bg)

    def set(self, n: int):
        digit = n % 10
        self.reset()
        self.DIGITS[digit].set(self.fg)
        tens = n // 10 % 10
        if tens:
            self.TENS[tens].set(self.fg)
            for i in range(1, tens):
                self.TENS[i].set(self.fg)
        hundreds = n // 100 % 10
        if hundreds == 0:
            keyboard.game_mode_led = False
            keyboard.macro_mode_led = False
        elif hundreds == 1:
            keyboard.game_mode_led = True
            keyboard.macro_mode_led = False
        elif hundreds == 2:
            keyboard.game_mode_led = False
            keyboard.macro_mode_led = True
        elif hundreds == 3:
            keyboard.game_mode_led = True
            keyboard.macro_mode_led = True


Counter.DIGITS = {
    0: SyncGroup(*Counter.get_segments('123567')),
    1: SyncGroup(*Counter.get_segments('36')),
    2: SyncGroup(*Counter.get_segments('13457')),
    3: SyncGroup(*Counter.get_segments('13467')),
    4: SyncGroup(*Counter.get_segments('2346')),
    5: SyncGroup(*Counter.get_segments('12467')),
    6: SyncGroup(*Counter.get_segments('124567')),
    7: SyncGroup(*Counter.get_segments('136')),
    8: SyncGroup(*Counter.get_segments('1234567')),
    9: SyncGroup(*Counter.get_segments('12346'))
}


# c=Counter(white,magenta)
# keyboard.brightness=70
# for i in range(20):
#     c.set(i)
#     render()
#     time.sleep(0.5)

class GameOver(Exception): pass


def print_array(arr):
    for row in arr:
        for col in row:
            print(f'({col[0]:^3} {col[1]:^3} {col[2]:^3})', end=' ')
        print()


class Frame:
    def __init__(self, character_color: Color, obstacle_color: Color, border_color: Color, bg: Color, arr=None):
        if arr is not None:
            self.game_area = arr
        else:
            self.game_area = np.zeros((4, 10, 3), np.uint8)
            self.game_area[:, :] = bg.r, bg.g, bg.b
        self.char_col = character_color
        self.ob_col = obstacle_color
        self.bo_col = border_color
        self.bg = bg

    def write_to_keyboard(self, keyboard=keyboard):
        keyboard.fx.advanced.matrix._matrix[:, 1:5, 3:13] = self.game_area.transpose((2, 0, 1))
        color = np.array([self.bo_col.r, self.bo_col.g, self.bo_col.b], ).reshape((3, 1))
        keyboard.fx.advanced.matrix._matrix[:, 0, 1:15] = color
        keyboard.fx.advanced.matrix._matrix[:, 5, 1:15] = color
        keyboard.fx.advanced.matrix._matrix[:, 1:6, 1] = color
        keyboard.fx.advanced.matrix._matrix[:, 1:6, 14] = color

        return self

    def write_to_curses(self, window: curses.window):

        window.addstr(0, 0, '\u2594' * 28)
        window.addstr(5, 0, '\u2581' * 28)
        for y in range(0, 6):
            window.addstr(y, 0, '\u258f')
        for y in range(0, 6):
            window.addstr(y, 28, '\u2595')

        bg = np.array((self.bg.r, self.bg.g, self.bg.b))
        char = np.array((self.char_col.r, self.char_col.g, self.char_col.b))
        ob = np.array((self.ob_col.r, self.ob_col.g, self.ob_col.b))
        for y, row in enumerate(self.game_area):
            for x, col in enumerate(row):
                if np.any(col != bg):
                    if np.all(col == char):
                        window.addch(y + 1, (x + 2) * 2, '\u2591', )
                    else:
                        window.addch(y + 1, (x + 2) * 2, '\u2588')

        return self

    def next(self, char_height: int, ob_height: int):
        ga = np.roll(self.game_area, -1, 1)
        ga[:, 9] = self.bg.r, self.bg.g, self.bg.b
        if np.all(ga[3 - char_height, 0] == (self.ob_col.r, self.ob_col.g, self.ob_col.b)):
            raise GameOver
        else:
            ga[3 - char_height, 0] = (self.char_col.r, self.char_col.g, self.char_col.b)
        if ob_height:
            ga[4 - ob_height:, 9] = np.array([self.ob_col.r, self.ob_col.g, self.ob_col.b], )
        return Frame(self.char_col, self.ob_col, self.bo_col, self.bg, ga)

    def __str__(self):
        return str(self.game_area)


class GameManager:
    def __init__(self):
        self.frame = Frame(green, magenta, white, off)
        self.character_position = 0
        self.frame_count = 0
        self.move_up = False
        self.last_ob = 0

    def next_frame(self, p=0.25):
        if self.move_up:
            if self.character_position == 3:
                self.move_up = False
            else:
                self.character_position += 1
        else:
            if self.character_position != 0:
                self.character_position -= 1

        if self.frame_count - self.last_ob > 7:
            gen = random.random() < p
            if gen:
                self.frame = self.frame.next(self.character_position, random.randint(1, 2))
                self.last_ob = self.frame_count
            else:
                self.frame = self.frame.next(self.character_position, 0)
        else:
            self.frame = self.frame.next(self.character_position, 0)
        self.frame_count += 1

    def up(self):
        self.move_up = True

    def reset(self):
        self.__init__()


def main(win: curses.window):
    keyboard.brightness = 80
    gm = GameManager()
    win.clear()
    win.nodelay(True)
    curses.start_color()
    curses.use_default_colors()
    start = time()
    gg = False
    counter = Counter(white, magenta)
    arrows = SyncGroup(UP_ARROW, DOWN_ARROW, LEFT_ARROW, RIGHT_ARROW)
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 2, i, 0)
    while True:
        c = win.getch()
        if c == ord('q'):
            break
        else:
            if c != -1:
                gm.up()
                if gg:
                    gg = False
                    gm = GameManager()
                else:
                    UP_ARROW.set(green)
                    render()
            else:
                arrows.set(Color(120, 255, 144))
            if not gg:
                if round(time() - start, 2) * 100 % 5 == 0:
                    win.clear()
                    try:
                        gm.next_frame()
                        gm.frame.write_to_keyboard()
                        gm.frame.write_to_curses(win)
                    except GameOver:
                        win.addstr(2, 5, 'Game Over. You scored ' + str(gm.frame_count // 5))
                        win.addstr(3, 5, 'Press q to quit, press anything else to restart')
                        gg = True
                        keyboard.fx.advanced.matrix.reset()
                        counter.set(gm.frame_count // 5)
                        Frame(red, red, red, red).write_to_keyboard()
                        SyncGroup(*get_keys('#$%edcvbg*()ik,./;')).set(yellow)
                        render()
                    else:
                        win.addstr(3, 34, f'Score: {gm.frame_count // 5}')

                    counter.set(gm.frame_count // 5)
                    render()

                    win.move(0, 0)
                    win.refresh()


if __name__ == '__main__':
    curses.wrapper(main)
