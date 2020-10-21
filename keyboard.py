from openrazer.client import DeviceManager

manager = DeviceManager()
keyboard = manager.devices[0]


class Color:
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b


white = Color(255, 255, 255)
magenta = Color(255, 0, 255)
green = Color(0, 255, 0)
blue = Color(0, 0, 255)
yellow = Color(255, 255, 0)
red = Color(255, 0, 0)
off = Color(0, 0, 0)


class Key:
    registered_keys = {}

    def __init__(self, row, col, name=''):
        self.row = row
        self.col = col
        self.name = name
        self.registered_keys[name] = self

    def set(self, color: Color):
        keyboard.fx.advanced.matrix[self.row, self.col] = (color.r, color.g, color.b)

    def __repr__(self):
        return f"<Key {self.name}>"


class SyncGroup:
    def __init__(self, *keys):
        self.keys = keys

    def set(self, color: Color):
        for key in self.keys:
            key.set(color)

    def __repr__(self):
        return "<SyncGroup " + ','.join(map(str, self.keys)) + ">"


class ExclusiveGroup:
    def __init__(self, *keys):
        self.keys = keys

    def set(self, idx: int, color: Color):
        for i, k in enumerate(self.keys):
            if i == idx:
                k.set(color)
            else:
                k.set(off)


ESC = Key(0, 1, "ESC")
F1 = Key(0, 3, "F1")
F2 = Key(0, 4, "F2")
F3 = Key(0, 5, "F3")
F4 = Key(0, 6, "F4")
F5 = Key(0, 7, "F5")
F6 = Key(0, 8, "F6")
F7 = Key(0, 9, "F7")
F8 = Key(0, 10, "F8")
F9 = Key(0, 11, "F9")
F10 = Key(0, 12, "F10")
F11 = Key(0, 13, "F11")
F12 = Key(0, 14, "F12")

PRT_SC = Key(0, 15, "PRT_SC")
SCR_LK = Key(0, 16, "SCR_LK")
PAUSE = Key(0, 17, "PAUSE")

TILDE = Key(1, 1, "~")
EXCLAMATION_MARK = Key(1, 2, "!")
AMPERSAT = Key(1, 3, "@")
OCTOTHORP = Key(1, 4, "#")
DOLLAR = Key(1, 5, "$")
PERCENT = Key(1, 6, "%")
CARET = Key(1, 7, "^")
AMPERSAND = Key(1, 8, "&")
ASTERISK = Key(1, 9, "*")
LEFT_PARENTHESIS = Key(1, 10, "(")
RIGHT_PARENTHESIS = Key(1, 11, ")")
UNDERSCORE = Key(1, 12, "_")
PLUS = Key(1, 13, "+")
BACKSPACE = Key(1, 14, "BACKSPACE")

INSERT = Key(1, 15, "INSERT")
HOME = Key(1, 16, "HOME")
PAGE_UP = Key(1, 17, "PAGE_UP")

NUM_LK = Key(1, 18, "NUM_LK")
NUM_SLASH = Key(1, 19, "NUM_SLASH")
NUM_ASTERISK = Key(1, 20, "NUM_ASTERISK")
NUM_MINUS = Key(1, 21, "NUM_MINUS")
NUM_7 = Key(2, 18, "7")
NUM_8 = Key(2, 19, "8")
NUM_9 = Key(2, 20, "9")
NUM_PLUS = Key(2, 21, "NUM_PLUS")
NUM_4 = Key(3, 18, "4")
NUM_5 = Key(3, 19, "5")
NUM_6 = Key(3, 20, "6")
NUM_1 = Key(4, 18, "1")
NUM_2 = Key(4, 19, "2")
NUM_3 = Key(4, 20, "3")
NUM_0 = Key(5, 19, "0")
NUM_DEL = Key(5, 20, "NUM_DEL")
NUM_ENTER = Key(4, 21, "NUM_ENTER")

TAB = Key(2, 1, "TAB")
Q = Key(2, 2, "Q")
W = Key(2, 3, "W")
E = Key(2, 4, "E")
R = Key(2, 5, "R")
T = Key(2, 6, "T")
Y = Key(2, 7, "Y")
U = Key(2, 8, "U")
I = Key(2, 9, "I")
O = Key(2, 10, "O")
P = Key(2, 11, "P")
LEFT_BRACKET = Key(2, 12, "[")
RIGHT_BRACKET = Key(2, 13, "]")
BACKSLASH = Key(2, 14, "\\")

DEL = Key(2, 15, "DEL")
END = Key(2, 16, "END")
PAGE_DOWN = Key(2, 17, "PAGE_DOWN")

CAPS_LOCK = Key(3, 1, "CAPS_LOCK")
A = Key(3, 2, "A")
S = Key(3, 3, "S")
D = Key(3, 4, "D")
F = Key(3, 5, "F")
G = Key(3, 6, "G")
H = Key(3, 7, "H")
J = Key(3, 8, "J")
K = Key(3, 9, "K")
L = Key(3, 10, "L")
SEMICOLON = Key(3, 11, ";")
QUOTE = Key(3, 12, "'")
ENTER = Key(3, 14, "ENTER")

LEFT_SHIFT = Key(4, 1, "LEFT_SHIFT")
Z = Key(4, 3, "Z")
X = Key(4, 4, "X")
C = Key(4, 5, "C")
V = Key(4, 6, "V")
B = Key(4, 7, "B")
N = Key(4, 8, "N")
M = Key(4, 9, "M")
COMMA = Key(4, 10, ",")
PERIOD = Key(4, 11, ".")
FORWARD_SLASH = Key(4, 12, "/")
RIGHT_SHIFT = Key(4, 14, "RIGHT_SHIFT")

UP_ARROW = Key(4, 16, "UP_ARROW")

LEFT_CONTROL = Key(5, 1, "LEFT_CONTROL")
WINDOWS = Key(5, 2, "WINDOWS")
LEFT_ALT = Key(5, 3, "LEFT_ALT")
SPACE = Key(5, 7, " ")
RIGHT_ALT = Key(5, 11, "RIGHT_ALT")
FN = Key(5, 12, "FN")
OPTION = Key(5, 13, "OPTION")
RIGHT_CONTROL = Key(5, 14, "RIGHT_CONTROL")

LEFT_ARROW = Key(5, 15, "LEFT_ARROW")
DOWN_ARROW = Key(5, 16, "DOWN_ARROW")
RIGHT_ARROW = Key(5, 17, "RIGHT_ARROW")


def get_key(symbol: str):
    return Key.registered_keys[symbol.upper()]


def get_keys(iterable):
    return tuple(map(get_key, iterable))
