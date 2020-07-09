if __name__ == "__main__":
    import shared
else:
    from helpers import shared
import curses
import json
import urllib3

const = shared.constants()
https = urllib3.PoolManager()

def select():
    versions = version_list()
    return curses.wrapper(versions.display)
class version_list():
    def __init__(self):
        self._version_list=[]
        self._selected = 0
        
        manifest = json.loads(https.request('GET',const.MANIFEST_URL).data.decode("utf-8"))
        for version in manifest["versions"]:
            self._version_list.append(version["id"])

    def display(self, stdscr):
        rows, cols = stdscr.getmaxyx()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self._window = [0, rows - 1]
        while True:
            stdscr.erase()
            for i in range(self._window[0], self._window[1]):
                if self._selected == i:
                    stdscr.addstr(self._version_list[i]+"\n", curses.A_STANDOUT)
                else:
                    stdscr.addstr(self._version_list[i]+"\n")
            stdscr.refresh()
            key = stdscr.getch()
            keydict = {
                curses.KEY_DOWN:self.key_down,
                curses.KEY_UP:self.key_up
                }
            if key in keydict:
                keydict[key]()
            if key == curses.KEY_ENTER or key == 10 or key == 13:
                return self._version_list[self._selected]

    def key_up(self):
        if self._window[0] == self._selected:
            if self._window[0] > 0:
                self._window[0] -= 1
                self._window[1] -= 1
                self._selected -= 1
        else:
            self._selected -= 1
    def key_down(self):
        if self._window[1] == self._selected+1:
            if self._window[1] < len(self._version_list):
                self._window[0] += 1
                self._window[1] += 1
                self._selected += 1
        else:
            self._selected += 1
if __name__ == "__main__":
    print(select())