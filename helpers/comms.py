import shared

from gi.repository import GLib
import subprocess
from pydbus import SessionBus as UsedBus  # TODO: replace with system

interface_name = "com.salernosection.mc_as_a_service.manager"
bus = UsedBus()
const = shared.constants()
try:
    manager = bus.get(const.INTERFACE)
except GLib.Error:
    print("error connecting to service")
    exit(1)


def blank():
    pass


def quiet_print(func):
    def inner(*args, **kwargs):

        if not kwargs["no_output"]:
            qprint = print
        else:
            qprint = blank
        del kwargs["no_output"]
        func(*args, **kwargs, printer=qprint)
    return inner


@quiet_print
def set_eula(self):
    """
    Returns:
        bool: returns whether or not the user has agreed to the eula
    """
    try:
        subprocess.run([const.APPS_PATH+"/eula.sh"], cwd=const.ROOT_PATH,
                       check=True)
    except subprocess.CalledProcessError:
        print("Did not agree to EULA")
        agree = False
    else:
        print("agreed to EULA")
        agree = True
    return agree


@quiet_print
def mc_version(self, *args, printer=print):
    mc_version = manager.mc_version
    printer(mc_version)
    return mc_version


@quiet_print
def start(self, *args, printer=print):
    started = manager.start()
    if started:
        printer("Started server")
    else:
        printer("Could not start server!")
    return started


@quiet_print
def stop(self, *args, printer=print):
    stopped = manager.stop()
    if stopped:
        printer("Stopped server")
    else:
        printer("Could not stop server!")
    return stopped


@quiet_print
def ramdisk(self, *args, printer=print):
    if args:
        manager.ramdisk = args[0]
    else:
        printer("ramdisk is "+("on" if manager.ramdisk else "off"))
    return manager.ramdisk


@quiet_print
def set_property(self, key, value=None, printer=print):
    properties = manager.server_properties
    if value is None:
        if key in properties:
            del properties[key]
    elif type(value) is str:
        properties[key] = value
    else:
        raise TypeError("Value must be str or None")
    manager.server_properties = properties


@quiet_print
def get_eula(self, *args, printer=print):
    return manager.eula


@quiet_print
def send(self, *args, printer=print):
    seperator = " "
    argString = seperator.join(args)
    return manager.send(argString)


@quiet_print
def status(self, *args, printer=print):
    return manager.status()


@quiet_print
def install(self, *args, printer=print):
    pass


@quiet_print
def set_path(self, *args, printer=print):
    pass
