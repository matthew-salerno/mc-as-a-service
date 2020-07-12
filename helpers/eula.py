if __name__ == "__main__":
    import shared
else:
    from helpers import shared
import curses
import urllib3
import json
import re
import textwrap
from time import sleep
from html.parser import HTMLParser

https = urllib3.PoolManager()
const = shared.constants()

# NOTE TODO: This file is a huge mess cobbled together quickly and without much thought.
# I plan on eventually rewriting and documenting it but for now it is fairly low
# priority. On a high level all it does is read the eula to the user and return
# true or false depending on what they answer.
# In short:
# I know my O values are terible
# I know this needs more comments
# I know this is not readable
# I will get around to it *eventually* 

class eula():
    def __init__(self):
        self.strings=[""]
        self.format = {"h1":False, "h2":False, "ul":False, "strong":False}
    def addstr(self, string):
        self.strings.append(string)
    def printall(self):
        for string in self.strings:
            print(string,end='',sep='')
    
    def get_string(self, cols):
        working_string = ''
        full_string = ''
        formatted_split = []
        for string in self.strings:
            full_string += string
        strings_split = full_string.split("\n")
        for string in strings_split:
            formatted_split.append(textwrap.fill(string, cols, replace_whitespace=False))
        working_string = '\n'.join(formatted_split)
        return re.split('<|>',working_string)
    
    def curse_all(self, obj, stdscr, pos=0):
        num_cols = obj.getmaxyx()[1]
        lines, cols = stdscr.getmaxyx()

        for string in self.get_string(num_cols - 1):
            
            if string in self.format:
                self.format[string]=True
                continue
            elif string[0]=='/' and len(string) < 10:
                string = string.lstrip('/')
                if string in self.format:
                    self.format[string]=False
                continue
            if self.format["h1"] or self.format["h2"]:
                half_length_of_message = int(len(string) / 2)
                y_position = obj.getyx()[0]
                middle_column = int(num_cols / 2)
                x_position = middle_column - half_length_of_message
                obj.addstr(y_position, x_position, string, curses.A_BOLD | curses.A_UNDERLINE)
            elif self.format["ul"] and self.format["strong"]:
                obj.addstr(string, curses.A_UNDERLINE)
            elif self.format["ul"]:
                obj.addstr(string, curses.A_UNDERLINE)
            elif self.format["strong"]:
                obj.addstr(string, curses.A_BOLD)
            else:
                obj.addstr(string)
        obj.refresh(0,0,1,1,lines - 2, cols - 1)
            
    def get_lines(self):
        lines=0
        for string in self.strings:
            lines += string.count('\n')
        return lines
    def get_lines_formatted(self, cols):
        return ''.join(self.get_string(cols)).count('\n')
        
class EULA_HTML_Parser(HTMLParser):
    def __init__(self, print_func=print):
        super().__init__()
        self.display=print_func
        self._on = False
        self._on_tag = 'div'
        self._on_attr = ('id', 'terms-text')
        self._off_tag = 'div'
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == self._on_tag:
            if self._on_attr in attrs:
                self._on = True
                return
        if not self._on:
            return
        # get links
        if tag == "a":
            for attr in attrs:
                if attr[0] == "href":
                    self.links.append(attr[1])

        self.tagger(tag, True)

    def handle_endtag(self, tag):
        if not self._on:
            return
        if tag == self._off_tag:
            self._on = False
            for i in range(len(self.links)):  # add links at the end
                self.links[i] = f"[{i+1}]{self.links[i]}\n"
                self.display(self.links[i])
            return
        self.tagger(tag, False)

    def handle_data(self, data):
        if self._on:
            self.display(data)
    def tagger(self, tag, start):
        if not self._on:
            return
        start_dict={
            "p":"    ",
            "li":"* ",
            "a":"<ul>",
            "h1":"\n\n<h1>",
            "h2":"\n<h2>"
        }
        end_dict={
            "p":"",
            "li":"",
            "a":f"[{len(self.links)}]</ul>"
        }
        tag_dict=(start_dict if start else end_dict)
        if tag in tag_dict:
            self.display(tag_dict[tag])
        else:
            self.display("<")
            self.display("/") if not start else ""
            self.display(tag)
            self.display(">")

def eula_check(stdscr):
    lines, cols = stdscr.getmaxyx()
    the_eula=eula()
    parser = EULA_HTML_Parser(the_eula.addstr)
    parser.feed(https.request('GET',const.EULA_URL).data.decode("utf-8"))
    pos = 0
    agree = False
    curses.curs_set(0)
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    eulapad = curses.newpad(the_eula.get_lines_formatted(curses.COLS-2)+1,curses.COLS-1)
    the_eula.curse_all(eulapad,stdscr)
    while True:
        stdscr.addstr(lines - 1,4,"I agree", curses.A_STANDOUT if agree else 0)
        stdscr.addstr(lines - 1, cols - 19,"I do not agree", 0 if agree else curses.A_STANDOUT)
        stdscr.refresh()
        eulapad.refresh(pos,0,1,1,lines - 2, cols - 1)
        key = stdscr.getch()
        if key == curses.KEY_UP and pos > 0:
            pos -= 1
        elif key == curses.KEY_DOWN and pos < eulapad.getmaxyx()[0] - lines + 2:
            pos += 1
        elif key == curses.KEY_RIGHT:
            agree = False
        elif key == curses.KEY_LEFT:
            agree = True
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            break
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    return agree

if __name__ == "__main__":
    print(curses.wrapper(eula_check))