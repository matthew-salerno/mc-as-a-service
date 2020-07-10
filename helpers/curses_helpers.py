import curses
from curses.textpad import Textbox, rectangle


class item_editor():
    def __init__(self, key, value, on_change=None, max_val_len=20):
        self.key=key
        self.value=value
        if type(value) is str:
            self.validation = self.str_validator
        elif type(value) is int:
            self.validation = self.int_validator
        elif type(value) is float:
            self.validation = self.float_validator
        self.max_val_len = max_val_len
    def display(self, y_pos, key_x, value_x, stdscr, selected, formatting=0):
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        key_window=curses.newwin(1,len(self.key)+1,y_pos,key_x)
        value_window=curses.newwin(1,self.max_val_len,y_pos,value_x)
        changed=False
        if selected:
            if type(self.value) is bool:
                self.bool_validator(stdscr,value_window)
            else:
                curses.curs_set(1)
                self.box = Textbox(value_window)
                self.box.edit(self.validation)
                self.box=None
            changed=True
        key_window.addstr(0,0,self.key, formatting)
        value_window.erase()
        value_window.addstr(str(self.value), formatting)
        key_window.refresh()
        value_window.refresh()
        del key_window
        del value_window
        return self.value if changed else None
    
    def str_validator(self, key):
        if self.box == None:
            return
        if key == 27:
            return curses.ascii.BEL
        elif key == curses.KEY_BACKSPACE or key == 127:
            return 8
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.value=self.box.gather().strip()
            return curses.ascii.BEL
        else:
            return key
    def float_validator(self, key):
        if self.box == None:
            return
        if key == 27:
            return curses.ascii.BEL
        elif key == curses.KEY_BACKSPACE or key == 127:
            return 8
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.value=float(self.box.gather().strip())
            return curses.ascii.BEL
        elif key == 46:
            gather = self.box.gather()
            # If dot hasn't been used and the string isn't empty
            if (not '.' in gather) and (gather.strip()):
                return key
        if key in range(48,58):  # allowed values
            return key
    def int_validator(self, key):
        if self.box == None:
            return
        if key == 27:
            return curses.ascii.BEL
        elif key == curses.KEY_BACKSPACE or key == 127:
            return 8
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self.value=int(self.box.gather().strip())
            return curses.ascii.BEL
        if key in range(48,58):  # allowed values
            return key
    def bool_validator(self, stdscr, window):  # This one's special and runs without textbox
        value = self.value
        while True:
            key = stdscr.getch()
            if key == 27:
                return value
            elif key in [curses.KEY_UP, curses.KEY_DOWN, 
               curses.KEY_LEFT, curses.KEY_RIGHT, 32]:  # 32 is space
                value = not value
                window.erase()
                window.addstr(str(value), curses.A_STANDOUT)
                window.refresh()
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                self.value = value
                return value

class list_editor():
    def __init__(self, items):
        self.itemlist = items
        self.items = []
    def display(self, stdscr):
        for item in self.itemlist:
            self.items.append(item_editor(item[0],item[1]))
        keylength = max(map(len, (item[0] for item in self.itemlist)))
        middle_col = int(stdscr.getmaxyx()[1]/2)
        stdscr.erase()
        stdscr.refresh()
        selected = 0
        edit = 0
        while True:
            for i in range(len(self.items)):
                self.items[i].display(i,middle_col-(keylength+2),middle_col+2,stdscr, i==selected and edit, curses.A_STANDOUT if i==selected else 0)
            edit = 0
            key = stdscr.getch()
            if key == curses.KEY_DOWN:
                selected = (selected + 1)%len(self.items)
            elif key == curses.KEY_UP:
                selected = (selected - 1)%len(self.items)
            elif key == curses.KEY_ENTER or key == 10 or key == 13:
                edit = 1

                
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
class 