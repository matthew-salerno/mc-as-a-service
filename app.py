from helpers import shared, commands, curses_helpers
from getopt import getopt, GetoptError
import pkg_resources
import curses
import sys
const = shared.constants()


def main(arguments):
    try:
        opts, args = getopt(arguments, "hvq", ["mc-version", "help", "quiet",
                                               "version"])
    except GetoptError:
        print(f"Wrong arguments, type {const.NAME} -h for help")
    option_dict = {
                "-h": cmd_help,
                "-v": version,
                "-q": quiet,
                "--mc-version": commands.mc_version,
                "--help": cmd_help, 
                "--quiet": quiet,
                "--version": version
                }
    if opts:  # if not empty
        # for this particular application we don't need a case where
        # there are multiple options or option values
        option_dict[opts[0][0]](args)
    else:
        args_processor(args)


def version(args):
    print(const.VERSION)


def quiet(args):
    args_processor(args, True)


def args_processor(args, quiet=False):
    args_dict = {
                "start": commands.start,
                "stop": commands.stop,
                "ramdisk": commands.ramdisk,
                "set-property": commands.set_property,
                "launch-path": commands.set_path,
                "eula": commands.set_eula,
                "get-eula": commands.get_eula,
                "send": commands.send,
                "status": commands.status,
                "install": commands.install,
                "launch-options": commands.launch_options,
                "connect": commands.connect
                }
    if len(args):
        if args[0] in args_dict:
            args_dict[args[0]](args[1:], printer=(commands.blank if quiet else print))
        else:
            print("No command found!")
    else:
        tui()


def cmd_help(args):
    helpstring = pkg_resources.resource_string(__name__, const.HELP_PATH.name).decode("utf-8")
    print(f"{const.NAME}: Version {const.VERSION}")
    print(helpstring)


def tui():
    while True:
        menu_items = {
                    "Start":commands.start,
                    "Stop":commands.stop,
                    "Console":commands.connect,
                    "Launch Options":commands.tui_launch_options,
                    "Server Options":commands.tui_server_options,
                    "Install":commands.install,
                    "Eula":commands.set_eula
                    }
        selector = curses_helpers.select_v(list(menu_items))
        selected = curses.wrapper(selector.display)
        if selected == None:
            break
        menu_items[selected](printer=commands.blank)  

if __name__ == "__main__":
    main(sys.argv[1:])