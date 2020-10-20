from keyboard import *
from itertools import chain
from time import sleep, time
import numpy as np
import random
import curses
from normal import  normal


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
                        window.addch(y + 1, (x + 2) * 2, '\u2591',)
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
            gen = random.random() > p
            if gen:
                self.frame = self.frame.next(self.character_position, random.randint(1, 2))
                self.last_ob = self.frame_count
            else:
                self.frame = self.frame.next(self.character_position, 0)
        else:
            self.frame = self.frame.next(self.character_position, 0)
        self.frame_count += 1
        render()

    def up(self):
        self.move_up = True

    def reset(self):
        self.__init__()


class AutomatedGameManager(GameManager):
    def __init__(self, targets: list):
        super().__init__()
        self.targets_stack = targets.copy()  # Targets is a sequence of frames to jump at
        self.targets_stack.sort(reverse=True)

    def next_frame(self, p=0.25):
        if self.move_up:
            if self.character_position == 2:
                self.move_up = False
            else:
                self.character_position += 1
        else:
            if self.character_position != 0:
                self.character_position -= 1

        if self.targets_stack:
            next_target = self.targets_stack.pop()
            if next_target == self.frame_count + 8:
                self.frame = self.frame.next(self.character_position, random.randint(1, 2))
            else:
                if next_target > self.frame_count+8:
                    self.targets_stack.append(next_target)
                self.frame = self.frame.next(self.character_position, 0)
        else:
            self.frame = self.frame.next(self.character_position, 0)
        self.frame_count += 1


def main(win: curses.window):
    keyboard.brightness = 80
    gm = GameManager()
    win.clear()
    win.nodelay(True)
    curses.start_color()
    curses.use_default_colors()
    start = time()
    gg = True
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
                        gm.frame.write_to_curses(win)
                        gm.frame.write_to_keyboard()
                    except GameOver:
                        win.addstr(3, 5, 'Game Over. You scored ' + str(gm.frame_count // 5))
                        gg = True
                        keyboard.fx.advanced.matrix.reset()
                        counter.set(gm.frame_count // 5)
                        Frame(red, red, red, red).write_to_keyboard()
                        SyncGroup(*get_keys('#$%edcvbg*()ik,./;')).set(yellow)
                        render()
                    else:
                        win.addstr(3, 34, f'Score: {gm.frame_count // 5}')
                    win.move(0, 0)
                    win.refresh()

                    counter.set(gm.frame_count // 5)


# curses.wrapper(main)


def show_animation(gwin:curses.window):
    global targets
    targets=list(map(lambda n: round(n * frame_rate), targets))
    targets.sort(reverse=True)
    gm = AutomatedGameManager(targets)
    c=Counter(white,magenta)
    keyboard.fx.advanced.matrix.reset()
    SyncGroup(LEFT_ARROW, DOWN_ARROW, RIGHT_ARROW).set(Color(120, 255, 144))
    render()

    curses.start_color()
    curses.use_default_colors()
    gwin.clear()
    gwin.nodelay(True)
    win=curses.newwin(7,60,1,2)
    win.clear()
    win.nodelay(True)
    while win.getch()==-1:
        UP_ARROW.set(green)
        render()
        sleep(0.4)
        UP_ARROW.set(off)
        render()
        sleep(0.4)
    gm.frame.write_to_keyboard()
    UP_ARROW.set(Color(120, 255, 144))
    c.set(0)
    mat=keyboard.fx.advanced.matrix._matrix
    for i in range(16):
        m=mat.copy()
        m[:,:,:16-i].fill(0)
        try:
            m[:,:,17+i:].fill(0)
        except IndexError:
            pass
        keyboard.fx.advanced.matrix._matrix=m
        sleep(0.05)
        render()

    while targets:
        start=time()
        if win.getch()==ord('q'):return
        win.clear()
        gm.frame.write_to_keyboard()
        gm.frame.write_to_curses(win)
        if gm.frame_count==targets[-1]:
            targets.pop()
            gm.up()
            UP_ARROW.set(green)
            win.addstr(3,50,'Now')
        elif gm.frame_count==targets[-1]-1:
            win.addstr(3, 50, 'Next')
        else:
            UP_ARROW.set(Color(120, 255, 144))
        c.set(gm.frame_count//10)
        render()
        gm.next_frame()
        win.addstr(3, 34, f'Score: {gm.frame_count // 10}')
        # win.addstr(4, 50, str(1/frame_rate-(time()-start)))
        win.refresh()
        sleep(1/frame_rate-(time()-start))

    UP_ARROW.set(Color(120, 255, 144))
    for i in range(10):
        start = time()
        gm.frame.write_to_keyboard()
        c.set(gm.frame_count//10)
        render()
        gm.next_frame()
        win.addstr(3, 34, f'Score: {gm.frame_count // 10}')
        sleep(1/frame_rate-(start-time()))


normal()
input('Press enter to continue')
for i in range(5):
    keyboard.fx.advanced.matrix.reset()
    render()
    normal()
    sleep(0.1)
keyboard.fx.advanced.matrix.reset()
render()
c=ExclusiveGroup(ESC,*get_keys('~!@#EDCVBGT%^&*IUJKM,./'),FN,OPTION,RIGHT_CONTROL)
color=Color(120, 255, 144)
for i in range(len(c.keys)):
    c.set(i,color)
    render()
    sleep(0.1)
keyboard.fx.advanced.matrix.reset()
LEFT_ARROW.set(color)
render()
sleep(0.1)
DOWN_ARROW.set(color)
render()
sleep(0.1)
RIGHT_ARROW.set(color)
render()
sleep(0.1)
l=[ 2.3, 3.2, 4.0, 7.9, 8.4, 8.9, 9.6, 10.0, 10.4, 13.7, 14.7, 15.5, 16.3, 17.9, 19.3, 20.8, 22.2, 25.6, 26.3, 27.0, 27.8, 28.5, 30.6, 31.8, 33.4, 33.9, 34.4, 34.9, 36.1, 36.5, 37.2, 38.0, 38.7, 39.5, 40.2, 41.0, 45.6, 46.1, 46.7, 47.3, 48.4, 48.9, 49.4, 49.9, 50.4, 51.1, 51.7, 52.8, 53.6, 58.3, 59.1, 59.7, 61.2, 62.7, 63.4, 64.2, 65.0, 65.9, 67.4, 68.9, 70.4, 72.0, 73.5, 75.0, 75.8, 76.6, 77.4, 78.1, 79.8, 81.2, 82.8, 84.3, 85.9, 87.5, 88.2, 88.9, 89.8, 90.6, 92.0, 93.6, 95.2, 96.8, 98.3, 99.9, 100.6, 101.4, 102.1, 103.1, 104.4, 106.2, 107.8, 109.3, 110.8, 112.4, 113.2, 113.8, 114.5, 115.4, 119.2, 119.6, 120.0, 120.6, 121.2, 121.7, 122.1, 125.7, 126.5, 127.4, 127.9, 129.3, 130.7, 132.2, 133.0, 135.4, 136.8, 137.3, 137.9, 138.6, 139.4, 140.2, 141.8, 143.2, 146.4, 147.5, 149.3, 150.1, 150.9, 151.7, 152.5, 154.0, 155.5, 156.8, 157.3, 157.8, 158.3, 158.8, 159.9, 160.3, 160.7, 161.1, 161.7, 162.9, 163.5, 164.3, 164.9, 166.4, 167.8, 169.5, 170.5, 171.1, 172.4, 174.2, 174.8, 175.7, 176.4, 177.3, 178.5, 180.2, 181.8, 183.5, 185.0, 186.7, 187.3, 188.0, 188.8, 189.7, 191.3, 192.8, 193.5, 194.2, 195.1, 196.0, 196.8, 197.4, 198.2, 199.0, 199.7, 200.5, 201.3, 202.1, 205.2, 206.6, 208.3, 209.8, 211.4, 212.3, 212.9, 213.6, 214.5, 216.0, 217.6, 219.3, 220.8, 222.3, 224.1, 224.8, 225.4, 226.1, 226.9, 235.9, 237.7, 238.5, 240.3, 242.2, 243.9, 245.4, 249.0, 249.5, 250.2, 250.9, 251.7, 252.7, 253.3, 254.0, 254.8, 255.4, 256.2, 256.9, 257.9, 259.5, 260.8, 262.5, 263.1, 264.0, 265.5, 266.9, 268.5, 269.0, 269.4, 270.2, 271.6, 273.0, 274.0, 274.7, 275.5, 276.3, 277.7, 279.4, 281.0, 282.5, 284.1, 285.7, 286.4, 287.0, 287.9, 288.6, 290.3, 291.8, 293.5, 295.0, 296.6, 298.1, 298.8, 299.5, 300.4, 301.2, 302.7, 304.4, 305.8, 307.3, 308.9, 310.4, 311.2, 312.0, 312.7, 313.5, 315.2, 316.7, 318.2, 319.9, 321.4, 323.0, 323.8, 324.6, 325.3, 326.1]
for i in range(len(l)-1):
    if l[i+1]-l[i] < 0.5:
        print(i,l[i],l[i+1],l[i+1]-l[i])


targets=l
frame_rate=10
curses.wrapper(show_animation)

