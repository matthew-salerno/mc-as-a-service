import app_constants
import curses
import urllib3
import json
import re
import textwrap
from time import sleep
from html.parser import HTMLParser

https = urllib3.PoolManager()
const = app_constants.constants()

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
        self.strings=[]
    def addstr(self, string):
        if self.strings:
            string = self.strings[-1] + string  # Combine with newest
            self.strings.pop()  # remove newest
        for substring in re.split('(<[^>]*>)',string):
            substring=re.sub('\n','',substring)
            substring=re.sub(' +',' ',substring)
            # so long as it's not empty
            if substring and not re.match('^ *$',substring):
                self.strings.append(substring)  # add it back in

    def curse_all(self, pad, stdscr, pos=0):
        pad.erase()
        format_dict = {"<h1>":False, "<h2>":False, "<ul>":False, "<strong>":False, "<sup>":False}
        pad_cols = pad.getmaxyx()[1]
        lines, cols = stdscr.getmaxyx()
        
        for string in self.strings:
            # Find begin format
            if string[0] == '<':
                if string in format_dict:
                    format_dict[string]=True
                elif string == "<p>":
                    pad.addstr("    ")
                #find end format
                elif string[1]=='/' and len(string) < 10:
                    string = re.sub('/','',string)
                    if string in format_dict:
                        format_dict[string]=False
                    elif string == "<p>":
                        pad.addstr("\n")
                continue
            y_position, x_position = pad.getyx()
            string = textwrap.fill(string, pad_cols-2, initial_indent=' '*x_position, drop_whitespace=False)
            string = re.sub('\n ', '\n', string)
            string = string[x_position:]
            # apply formatting
            string_format = 0
            
            if not format_dict["<sup>"]:
                if format_dict["<h1>"] or format_dict["<h2>"]:  # Headers
                    string_format = string_format | curses.A_BOLD | curses.A_UNDERLINE
                    half_length_of_message = int(len(string) / 2)
                    middle_column = int(pad_cols / 2)
                    x_position = middle_column - half_length_of_message
                    y_position += 1
                    #pad.addstr("\n")  # This line shouldn't make a difference
                    string = string+"\n"
                if format_dict["<ul>"]:  # Underline
                    string_format = string_format | curses.A_UNDERLINE
                if format_dict["<strong>"]:  # Bold
                    string_format = string_format | curses.A_BOLD
            pad.addstr(y_position, x_position, string, string_format)
        # Refresh pad at top
        pad.refresh(pos,0,1,1,lines - 2, cols - 1)
            
    def get_lines(self, cols):
        fakepad = fake_pad(cols)
        fakescr = fake_pad(cols)
        self.curse_all(fakepad,fakescr)
        return fakepad.lines

class fake_pad():
    """A fake pad object which is used to count new lines printed
    Slower than it could be but it has the advantage of garrunteeing the right 
    answer no matter how much things in another function may change
    """
    def __init__(self, cols):
        self.cols = cols
        self.lines = 0

    def refresh(self, *args, **kwargs):
        pass

    def addstr(self, *args):
        if len(args) in [1,2]:
            y = self.lines
            # x = x pos
            string = args[0]
            # formatting = args[1]
        elif len(args) in [3,4]:
            y = args[0]
            # x = args[1]
            string = args[2]
            # formatting = args[3]
        else:
            raise ValueError("Wrong number of arguments!")
        if y > self.lines:
            self.lines = y
        self.lines += string.count("\n")

    def getyx(self):
        return (self.lines,0)

    def getmaxyx(self):
        return (self.lines,self.cols)

    def erase(self):
        self.lines = 0

    def clear(self):
        self.lines = 0

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
            # Add links to the end
            for i in range(len(self.links)):  # add links at the end
                self.links[i] = f"[{i+1}]{self.links[i]}</p>"
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
            "li":"<sup>* </sup>", # sup is my own tag, for suppress, it temporarily turns off tags
            "a":"<ul>",
        }
        end_dict={
            "li":"</p>",
            "a":f"</ul> [{len(self.links)}]"
        }
        tag_dict=(start_dict if start else end_dict)
        if tag in tag_dict:
            self.display(tag_dict[tag])
        else:
            self.display(f"<{'/' if not start else ''}{tag}>")

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
    eulapad = curses.newpad(the_eula.get_lines(cols-2)+10,cols-2)
    the_eula.curse_all(eulapad, stdscr, pos)
    while True:
        lines, cols = stdscr.getmaxyx()
        stdscr.addstr(lines - 1,4,"I agree", curses.A_STANDOUT if agree else 0)
        stdscr.addstr(lines - 1, cols - 19,"I do not agree", 0 if agree else curses.A_STANDOUT)
        stdscr.refresh()
        eulapad.refresh(pos,0,1,1,lines - 2, cols - 1)
        eula_length=eulapad.getmaxyx()[0]
        key = stdscr.getch()
        if key == curses.KEY_UP and pos > 0:
            pos -= 1
        elif key == curses.KEY_DOWN and pos < (eula_length - lines):
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