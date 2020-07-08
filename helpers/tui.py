import shared
import curses
import urllib3
import json
import re
import textwrap
from time import sleep
from html.parser import HTMLParser

http = urllib3.PoolManager()
const = shared.constants()

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
    
    def curse_all(self, obj, pos=0):
        for string in self.get_string(curses.COLS - 2):
            
            if string in self.format:
                self.format[string]=True
                continue
            elif string[0]=='/' and len(string) < 10:
                string = string.lstrip('/')
                if string in self.format:
                    self.format[string]=False
                continue
            if self.format["h1"] or self.format["h2"]:
                obj.addstr(string, curses.A_BOLD | curses.A_UNDERLINE)
            elif self.format["ul"] and self.format["strong"]:
                obj.addstr(string, curses.A_UNDERLINE)
            elif self.format["ul"]:
                obj.addstr(string, curses.A_UNDERLINE)
            elif self.format["strong"]:
                obj.addstr(string, curses.A_BOLD)
            else:
                obj.addstr(string)
        obj.refresh(0,0,1,1,curses.LINES - 2, curses.COLS - 1)
            
    
    def get_lines(self):
        lines=0
        for string in self.strings:
            lines += string.count('\n')
        return lines
    def get_lines_formatted(self, cols):  # NOTE: this may return a value larger than the real number of lines
        text = ''.join(self.strings)
        text = textwrap.fill(text, cols, replace_whitespace=False)
        return text.count('\n')
        

class MyHTMLParser(HTMLParser):
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

the_eula=eula()
parser = MyHTMLParser(the_eula.addstr)
parser.feed(http.request('GET',"https://account.mojang.com/documents/minecraft_eula").data.decode("utf-8"))

def main(stdscr):
    pos = 0
    curses.curs_set(0)
    stdscr.clear()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    print(str(the_eula.get_lines_formatted(curses.COLS-5))+"\n\n")
    eulapad = curses.newpad(the_eula.get_lines_formatted(curses.COLS-3),curses.COLS)
    
    the_eula.curse_all(eulapad)
    
    while True:
        stdscr.refresh()
        eulapad.refresh(pos,0,1,1,curses.LINES - 2, curses.COLS - 1)
        key = stdscr.getkey()
        if key == "KEY_UP" and pos > 0:
            pos -= 1
        elif key == "KEY_DOWN" and pos < eulapad.getmaxyx()[0] - curses.LINES + 2:
            pos += 1
        stdscr.addstr(curses.LINES - 1,0,"Pressed "+str(key))
        
    

    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
curses.wrapper(main)
