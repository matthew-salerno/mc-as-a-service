if __name__ == "__main__":
    import shared
else:
    from helpers import shared
import curses
import json
import urllib3

const = shared.constants()
https = urllib3.PoolManager()

def select(branch="ask"):
    if branch == "ask":
        branch = curses.wrapper(select_branch)
    versions = version_list(branch)
    return curses.wrapper(versions.display)
    
def select_branch(stdscr):
    rows, cols = stdscr.getmaxyx()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    selected=0
    branches=["Release","Snapshot","All"]
    while True:
        stdscr.erase()
        for i in range(len(branches)):
            # Get centered position
            half_length_of_message = int(len(" ".join(branches)) / 2)
            
            middle_column = int(cols / 2)
            middle_row = int(rows / 2)
            y_position = middle_row
            x_position = middle_column - half_length_of_message
            # Print
            if selected == i:
                stdscr.addstr(y_position, x_position +
                (sum(map(len,branches[0:i])))+i, branches[i], curses.A_STANDOUT)
            else:
                stdscr.addstr(y_position, x_position +
                (sum(map(len,branches[0:i])))+i, branches[i])
        stdscr.refresh()
        key = stdscr.getch()
        if key == curses.KEY_RIGHT:
            selected = (selected + 1)%len(branches)
        elif key == curses.KEY_LEFT:
            selected = (selected - 1)%len(branches)
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
                    return branches[selected]
    

class version_list():
    def __init__(self, branch="all"):
        self._version_list=[]
        self._selected = 0
        manifest = json.loads(https.request('GET',const.MANIFEST_URL).data.decode("utf-8"))
        for version in manifest["versions"]:
            if branch == "all":
                self._version_list.append(version["id"])
            elif branch == "snapshot":
                if version["type"] == "snapshot":
                    self._version_list.append(version["id"])
            elif branch == "release":
                if version["type"] == "release":
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
                # Get centered position
                half_length_of_message = int(len(self._version_list[i]) / 2)
                y_position = stdscr.getyx()[0]
                middle_column = int(cols / 2)
                x_position = middle_column - half_length_of_message
                # Print
                if self._selected == i:
                    stdscr.addstr(y_position, x_position,self._version_list[i]+"\n", curses.A_STANDOUT)
                else:
                    stdscr.addstr(y_position, x_position,self._version_list[i]+"\n")
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
    print(select("all"))
    print(select("release"))
    print(select("snapshot"))