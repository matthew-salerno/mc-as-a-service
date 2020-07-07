from helpers import constants
from apps import comms
from getopt import getopt, GetoptError

const = constants()


def main(arguments):
    try:
        opts, args = getopt(arguments, "hvq", ["mc-version", "help", "quiet",
                                               "version"])
    except GetoptError:
        print(f"Wrong arguments, type {const.NAME} -h for help")
    option_dict = {"-h": cmd_help, "-v": version, "-q": quiet,
                   "--mc-version": comms.mc_version, "--help": cmd_help,
                   "--quiet": quiet, "--version": version}
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
    args_dict = {"start": comms.start, "stop": comms.stop,
                 "ramdisk": comms.ramdisk, "property": comms.set_property,
                 "launch-path": comms.set_path, "eula": comms.set_eula,
                 "get-eula": comms.get_eula, "send": comms.send,
                 "status": comms.status, "install": comms.install}
    if args:
        args_dict[args[0]](args[1:], no_output=quiet)
    else:
        tui()


def cmd_help():
    pass


def tui():
    pass
