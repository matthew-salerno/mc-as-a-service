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
    """All this decorator does is supply a function for printing which
    prints nothing if no_output is true

    Args:
        func (function): the function to apply this decorator to
    """
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
    """Returns the minecraft game version

    Args:
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        str: the minecraft version
    """
    mc_version = manager.mc_version
    printer(mc_version)
    return mc_version


@quiet_print
def start(self, *args, printer=print):
    """Tells the minecraft server to start

    Args:
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: whether the start was successful
    """
    started = manager.start()
    if started:
        printer("Started server")
    else:
        printer("Could not start server!")
    return started


@quiet_print
def stop(self, *args, printer=print):
    """Tells the minecraft server to stop

    Args:
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: whether the server successfully stopped
    """
    stopped = manager.stop()
    if stopped:
        printer("Stopped server")
    else:
        printer("Could not stop server!")
    return stopped


@quiet_print
def ramdisk(self, *args, printer=print):
    """Changes the ramdisk option in the server config
    NOTE: This does not create a ramdisk, it simply
    assumes you have mounted a ramdisk to the ramdisk
    folder

    Args:
        *args[0] (bool, optional): if this is set it
            sets the ramdisk config to this value.
            If this is not set it makes no changes.
        
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: the state of the ramdisk after any changes
    """
    if args:
        manager.ramdisk = args[0]
    else:
        printer("ramdisk is "+("on" if manager.ramdisk else "off"))
    return manager.ramdisk


@quiet_print
def set_property(self, key, value=None, printer=print):
    """sets a property in server.properties

    Args:
        key (str): the property to set
            value (str, optional): The value to set the property to
            deletes the property if None. Defaults to None.
        
        printer (function, optional): The function to
            display text. Defaults to print.

    Raises:
        TypeError: Type error if the value is of the wrong type
    """
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
    """Returns whether or not the eula has been
    agreed to

    Args:
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: True if eula=true, false otherwise
    """
    return manager.eula


@quiet_print
def send(self, *args, printer=print):
    """Sends a command to the minecraft server

    Args:
        *args (str): the command to send, can be a string or list of strings
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: returns True if the message was sent, False otherwise.
            Note this does not mean the server recieved or understood the message
            it simply means the service got the message and sent a reply
    """
    seperator = " "
    argString = seperator.join(args)
    return manager.send(argString)


@quiet_print
def status(self, *args, printer=print):
    """Returns the status of the Minecraft server

    Args:
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: True if the server is running, false if it is not
    """
    return manager.status()


@quiet_print
def install(self, *args, printer=print):
    """[summary]

    Args:
        *args[1] (str, optional): The version to install,
            opens up the TUI installer if not specified
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        bool: True if the install was successful, False otherwise 
    """
    # TODO
    pass


@quiet_print
def path(self, *args, printer=print):
    """sets the path to the server launcher, relative to the server folder

    Args:
        *args[1] (str, optional): The path to the launcher to use, if None
            does not make any changes
        printer (function, optional): The function to
            display text. Defaults to print.

    Returns:
        str: returns the server path after any changes were made
    """
    # TODO
    pass
