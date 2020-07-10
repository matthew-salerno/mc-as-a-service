import curses
class select_h():
    def __init__(self, items, title=""):
        self.items = items
        self.title = title
    def display(self, stdscr):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        selected=0
        while True:
            rows, cols = stdscr.getmaxyx()
            middle_column = int(cols / 2)
            middle_row = int(rows / 2)
            half_length_of_message = int(len(self.title) / 2)
            x_position = middle_column - half_length_of_message
            stdscr.erase()
            stdscr.addstr(0, x_position, self.title+"\n", curses.A_BOLD)
            for i in range(len(self.items)):
                # Get centered position
                half_length_of_message = int(len(" ".join(self.items)) / 2)
                y_position = middle_row
                x_position = middle_column - half_length_of_message
                # Print
                if selected == i:
                    stdscr.addstr(y_position, x_position +
                    (sum(map(len,self.items[0:i])))+i, self.items[i], curses.A_STANDOUT)
                else:
                    stdscr.addstr(y_position, x_position +
                    (sum(map(len,self.items[0:i])))+i, self.items[i])
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_RIGHT:
                selected = (selected + 1)%len(self.items)
            elif key == curses.KEY_LEFT:
                selected = (selected - 1)%len(self.items)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                        return self.items[selected]

class select_v():
    def __init__(self, items, title=""):
        self.items = items
        self.title = title
    def display(self, stdscr):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        selected=0
        while True:
            rows, cols = stdscr.getmaxyx()
            middle_row = int(rows / 2)
            middle_column = int(cols / 2)
            top_row = middle_row-(len(self.items)/2)
            half_length_of_message = int(len(self.title) / 2)
            x_position = middle_column - half_length_of_message
            stdscr.erase()
            stdscr.addstr(0, x_position, self.title+"\n", curses.A_BOLD)
            for i in range(len(self.items)):
                # Get centered position
                half_length_of_message = int(len(self.items[i]) / 2)
                
                y_position = top_row
                x_position = middle_column - half_length_of_message
                # Print
                if selected == i:
                    stdscr.addstr(y_position+i, x_position, self.items[i], curses.A_STANDOUT)
                else:
                    stdscr.addstr(y_position+i, x_position, self.items[i])
            stdscr.refresh()
            key = stdscr.getch()
            if key == curses.KEY_DOWN:
                selected = (selected + 1)%len(self.items)
            elif key == curses.KEY_UP:
                selected = (selected - 1)%len(self.items)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                        return self.items[selected]

class select_v_scrolling():
    def __init__(self, items, title=""):
        self.items = items
        self.title = title
    def display(self, stdscr):
        rows, cols = stdscr.getmaxyx()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self._selected = 0
        self._window = [0, min(rows - 2,len(self.items))]
        while True:
            rows, cols = stdscr.getmaxyx()
            middle_column = int(cols / 2)
            half_length_of_message = int(len(self.title) / 2)
            x_position = middle_column - half_length_of_message
            stdscr.erase()
            stdscr.addstr(0, x_position, self.title+"\n", curses.A_BOLD)
            
            for i in range(self._window[0], self._window[1]):
                # Get centered position
                half_length_of_message = int(len(self.items[i]) / 2)
                y_position = stdscr.getyx()[0]
                x_position = middle_column - half_length_of_message
                # Print
                if self._selected == i:
                    stdscr.addstr(y_position, x_position,self.items[i]+"\n", curses.A_STANDOUT)
                else:
                    stdscr.addstr(y_position, x_position,self.items[i]+"\n")
            stdscr.refresh()
            key = stdscr.getch()
            keydict = {
                curses.KEY_DOWN:self.key_down,
                curses.KEY_UP:self.key_up
                }
            if key in keydict:
                keydict[key]()
            if key == curses.KEY_ENTER or key == 10 or key == 13:
                return self.items[self._selected]
    
    def key_up(self):
        if self._window[0] == self._selected:
            if self._window[0] > 1:
                self._window[0] -= 1
                self._window[1] -= 1
                self._selected -= 1
        else:
            self._selected -= 1

    def key_down(self):
        if self._window[1] == self._selected+1:
            if self._window[1] < len(self.items):
                self._window[0] += 1
                self._window[1] += 1
                self._selected += 1
        else:
            self._selected += 1