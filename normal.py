from keyboard import *

function_keys = SyncGroup(F1, F2, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12)
screen_controls = SyncGroup(PRT_SC, SCR_LK, PAUSE)
first_row = SyncGroup(TILDE, EXCLAMATION_MARK, AMPERSAT, OCTOTHORP, DOLLAR, PERCENT, CARET, AMPERSAND, ASTERISK,
                      LEFT_PARENTHESIS, RIGHT_PARENTHESIS, UNDERSCORE, PLUS, BACKSPACE)
top_row = SyncGroup(Q, W, E, R, T, Y, U, I, O, P, LEFT_BRACKET, RIGHT_BRACKET, BACKSLASH)
home_row = SyncGroup(CAPS_LOCK, A, S, D, F, G, H, J, K, L, SEMICOLON, QUOTE, ENTER)
bottom_row = SyncGroup(LEFT_SHIFT, Z, X, C, V, B, N, M, COMMA, PERIOD, FORWARD_SLASH, RIGHT_SHIFT)
space_row = SyncGroup(LEFT_CONTROL, WINDOWS, LEFT_ALT, SPACE, RIGHT_ALT, FN, OPTION, RIGHT_CONTROL)
control_keys = SyncGroup(INSERT, HOME, PAGE_UP, DEL, END, PAGE_DOWN)
arrow_keys = SyncGroup(UP_ARROW, DOWN_ARROW, LEFT_ARROW, RIGHT_ARROW)
num_keys = SyncGroup(NUM_0, NUM_1, NUM_2, NUM_3, NUM_4, NUM_5, NUM_6, NUM_7, NUM_8, NUM_9, NUM_LK, NUM_SLASH,
                     NUM_ASTERISK, NUM_MINUS, NUM_PLUS, NUM_DEL, NUM_ENTER)


def normal():
    keyboard.fx.advanced.matrix.reset()
    keyboard.game_mode_led = False
    keyboard.macro_mode_led = False
    ESC.set(magenta)
    function_keys.set(Color(102, 102, 255))
    screen_controls.set(yellow)
    first_row.set(white)
    top_row.set(white)
    home_row.set(white)
    control_keys.set(Color(0, 100, 100))
    bottom_row.set(white)
    arrow_keys.set(Color(120, 255, 144))
    space_row.set(white)
    num_keys.set(Color(250, 120, 255))

    keyboard.fx.advanced.draw()


if __name__ == '__main__':
    normal()
