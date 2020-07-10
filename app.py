from helpers import shared, comands
from getopt import getopt, GetoptError
import pkg_resources
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
                "--mc-version": comms.mc_version,
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


def version(*args):
    print(const.VERSION)


def quiet(*args):
    args_processor(args, True)


def args_processor(*args, quiet=False):
    args_dict = {
                "start": comands.start,
                "stop": comands.stop,
                "ramdisk": comands.ramdisk,
                "set-property": comands.set_property,
                "launch-path": comands.set_path,
                "eula": comands.set_eula,
                "get-eula": comands.get_eula,
                "send": comands.send,
                "status": comands.status,
                "install": comands.install,
                "launch-options": comands.launch_options
                }
    if args:
        args_dict[args[0]](args[1:], no_output=quiet)
    else:
        tui()  # TODO


def cmd_help():
    helpstring =  (pkg_resources.resource_string(__name__, const.HELP_PATH).decode("utf-8"))
    print(f"{const.NAME}: Version {const.VERSION}")
    print(helpstring)


def tui():
    pass # TODO
