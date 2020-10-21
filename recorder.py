from curses import wrapper
import curses
from time import time

rec=[]

def main(win:curses.window):
    # Clear screen
    win.clear()
    win.nodelay(True)
    win.addstr(0, 0, 'Press r to reset timer, q to quit')
    start=None
    while True:
        c = win.getch()
        if c == ord('p'):
            print(c)
        elif c == ord('q'):
            break  # Exit the while loop
        elif c==ord('r'):
            start=None
            rec.clear()
            win.addstr(1, 0, 'press another key to start')
        else:
            if start is not None:
                win.addstr(1, 0, str(round(time() - start, 2)))
            if c!=-1:
                if start is None:
                    win.clear()
                    win.addstr(0, 0, 'Press r to reset timer, q to quit')
                    start=time()
                t=round(time()-start,2)
                win.addstr(1, 10, str(t))
                rec.append(round(t*20)/20*2)
            win.refresh()
wrapper(main)

print(rec)

