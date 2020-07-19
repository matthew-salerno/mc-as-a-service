import service_constants, installer
import re
import json
import subprocess
from os import environ, chdir
from time import sleep, gmtime, strftime
from pydbus.generic import signal
import shutil
from pathlib import Path
from dirsync import sync
from gi.repository import GLib

const = service_constants.constants()

if const.SNAP:
    from pydbus import SystemBus as UsedBus
else:
    from pydbus import SessionBus as UsedBus

bus = UsedBus()
loop = GLib.MainLoop()
chdir(const.ROOT_PATH)
class manager(object):
    """Manages the various functions of a minecraft server, such as starting,
    stopping and configuring"""
    with const.XML_PATH.open() as xml:
        dbus = xml.read()
        xml.close()
    PropertiesChanged = signal()  # emit when a property changes
    server_changed = signal()  # emit when the server starts/stops

    def __init__(self, loop):
        super().__init__()
        self._loop = loop
        self._ramdisk_graceful_exit = True
        self._server_process = server()
        self._server_state = False
        # to querry the status of
        self.load_config()
        self.sync_properties()
        self.save_properties()
        #setup world path
        self._world_path = const.SERVER_DIR_PATH
        if "level-name" in self._config_data["server"]["properties"]:
            self._world_path /= (self._config_data["server"]["properties"]
                                 ["level-name"])
        elif "level-name" in self._config_data["server"]["default_properties"]:
            self._world_path /= (self._config_data["server"]
                                 ["default_properties"]
                                 ["level-name"])
        else:
            print("No level-name found!")
            self._world_path /= "world"

        self._ramdisk = ramdisk(self._server_process, self._world_path)

    # __del__ does not work for some reason
    def close(self):
        print("Finishing up...")
        self.sync_properties()
        self.save_properties()
        self.stop(120)
        self.save_config()
        print("Done")

    def load_config(self):
        config_path = const.CONFIG_PATH
        if not config_path.is_file():
            print("No config found, loading defaults")
            default_config_path = const.DEFAULT_CONFIG_PATH
            if default_config_path.exists():
                shutil.copy(default_config_path,config_path)
            else:
                raise FileNotFoundError("Config file and default config file could not be found!")
        config = config_path.open("r")
        self._config_data = json.load(config)
        # make sure server directory isn't escaped
        if (re.search(r"\.\.", self._config_data["launcher"]
                        ["launch_path"])
           is not None):
            raise ValueError("jarfile cannot contain \"..\"")
        if (re.search(r"/", self._config_data["launcher"]
                        ["launch_path"])
           is not None):
            raise ValueError("jarfile cannot contain \"/\"")
        if (re.search(r"\\", self._config_data["launcher"]
                        ["launch_path"])
           is not None):
            raise ValueError("jarfile cannot contain \"\\\"")
        config.close()

    def sync_properties(self):
        """adds properties from server.properties to default_config if default
        config does not constain a key for said property. Also adds properties
        to config if the property has changed since it was last loaded
        """
        if not const.PROPERTIES_PATH.exists():
            return
        # find new properties in server.properties
        with const.PROPERTIES_PATH.open('r') as properties:
            for line in properties.readlines():
                setting = re.match(r'(^[^#]*)=(.*[^#])', line, re.M)
                if setting is not None:
                    key, value = setting.groups()
                    value = re.sub(r'[\n$]', r'', value)
                    print(f"Found setting: \"{key}\" with value \"{value}\"")
                    # load new server properties into config defaults
                    if (key not in self._config_data["server"]
                       ["default_properties"] and key not in
                       self._config_data["server"]["properties"]):
                        self._config_data["server"]["default_properties"][key]\
                            = value
                        print("key not seen before, adding to default config")
                    # this nasty if statement just checks if the server's
                    # valuesare different from the json values for keys
                    # which are in both. This is used to add config changes
                    # from the server into the json.
                    # A foolish consistency is the hobgoblin of little minds
                    elif (((key in self._config_data["server"]
                            ["default_properties"]) and (self._config_data
                                                         ["server"]
                                                         ["default_properties"]
                                                         [key] != value)) or
                            ((key in self._config_data["server"]["properties"])
                             and
                             (self._config_data["server"]["properties"][key] !=
                             value))):
                        self._config_data["server"]["properties"][key] = value
                    # I am very foolish and have a tiny, tiny mind.
                    # But my linter is lookin' fine
            properties.close()

    def save_config(self):
        with const.CONFIG_PATH.open("w") as config:
            json.dump(self._config_data, config)
            config.close()
        return True

    def save_properties(self):
        with const.PROPERTIES_PATH.open('w') as properties:
            properties.write("#This file is autogenerated by " +
                             const.NAME + "\n")
            properties.write("#please make changes there\n")
            all_keys = (
                frozenset(self._config_data["server"]["properties"]) |
                frozenset(self._config_data["server"]["default_properties"])
            )
            for key in all_keys:
                if key in self._config_data["server"]["properties"]:
                    value = self._config_data["server"]["properties"][key]
                    properties.write(f"{key}={value}\n")
                elif key in self._config_data["server"]["default_properties"]:
                    value = (self._config_data["server"]["default_properties"]
                                              [key])
                    properties.write(f"{key}={value}\n")
                else:
                    raise KeyError(f"{key} not found in either properties")
            properties.close()
            if self.status():
                self.reload_properties()

    @property
    def launch_path(self):
        """
        Returns:
            str: the path, relative to the server directory, where the jarfile
            is located
        """
        return self._config_data["launcher"]["launch_path"]

    @launch_path.setter
    def launch_path(self, path):
        """sets the path of the jarfile to be executed

        Args:
            path (str): the path, relative to the server directory, to the
            jarfile
        """
        self._config_data["launcher"]["launch_path"] = path
        self.save_config()
        self.PropertiesChanged(const.INTERFACE, {"launch_path": path}, [])

    @property
    def launch_options(self):
        """
        Returns:
            list[str]: returns a list of options used when launching the server
        """
        return self._config_data["launcher"]["options"]

    @launch_options.setter
    def launch_options(self, options):
        """adds a launch option to be executed when the server starts (-Xmx=2G)

        Args:
            options (list[str]): the options to use, without the dash
            (["Xmx=2G","Xms=1G"])
        """
        self._config_data["launcher"]["options"] = options
        self.save_config()
        self.PropertiesChanged(const.INTERFACE, {"launch_options": options},
                               [])

    @property
    def server_properties(self):
        """
        Returns:
            dict{str:str}: returns a dict of keys and values for server options
        """
        return self._config_data["server"]["properties"]

    @server_properties.setter
    def server_properties(self, properties):
        """changes a property in the server.properties file
        (only changes before server launch)

        Args:
            properties: a dict containing the properties for the server
        """
        self._config_data["server"]["properties"] = properties
        self.save_properties()
        self.save_config()
        self.PropertiesChanged(const.INTERFACE,
                               {"server_properties": properties}, [])

    @property
    def server_default_properties(self):
        """
        Returns:
            dict{str:str}: returns a dict of keys and values for server options
        """
        return self._config_data["server"]["default_properties"]

    @property
    def eula(self):
        """
        Returns:
            bool: whether or not the user has agreed to the eula
        """
        try:
            eula_file = const.EULA_PATH.open("r")
        except IOError:
            return False
        agree = False
        for line in eula_file.readlines():
            if re.search("eula=true", line):
                agree = True
        eula_file.close()
        return agree

    @eula.setter
    def eula(self, value):
        eula_file = const.EULA_PATH.open("w")
        cur_time = strftime("%a %d %b %Y %H:%M:%S %Z", gmtime())
        eula_file.write(
            "#By changing the setting below to TRUE you are indicating your" +
            "agreement to our EULA" +
            "(https://account.mojang.com/documents/minecraft_eula).\n" +
            f"#{cur_time}\n")
        if value == True:
            eula_file.write("eula=true")
        else:
            eula_file.write("eula=false")
        self.PropertiesChanged(const.INTERFACE, {"eula": self.eula}, [])

    @property
    def mc_version(self):
        if "version" in self._config_data["server"]:
            return self._config_data["server"]["version"]
        else:
            return "None"

    @property
    def ramdisk(self):
        """
        Returns:
            bool: returns whether or not the ramdisk will be used
        """
        return self._config_data["ramdisk"]["enabled"]

    @ramdisk.setter
    def ramdisk(self, value):
        """sets whether or not to use a ramdisk

        Args:
            value (bool): true to use ramdisk, false otherwise

        Returns:
            bool: true if option successfully changed, false otherwise
        """
        self._config_data["ramdisk"]["enabled"] = value
        self.save_config()
        self.PropertiesChanged(const.INTERFACE, {"ramdisk": value}, [])

    @property
    def ramdisk_interval(self):
        """
        Returns:
            str: returns the filesystem used for the ramdisk
        """
        return self._config_data["ramdisk"]["interval"]

    @ramdisk_interval.setter
    def ramdisk_interval(self, time):
        """Sets the time in minutes between ramdisk backups
        Args:
            time (int): the number of minutes between backups
        """
        self._config_data["ramdisk"]["interval"] = time
        self.save_config()
        self.PropertiesChanged(const.INTERFACE, {"ramdisk_interval": time}, [])

    def install(self, version):
        """installs the selected version of the minecraft server

        Args:
            version (str): the version of minecraft to install, as used in the
            version manifest:
            https://launchermeta.mojang.com/mc/game/version_manifest.json

        Returns:
            bool: true if installed, false otherwise
        """
        if installer.install_server(version) is None:
            print("Install failed")
            return False
        else:
            self._config_data["server"]["version"] = version
            self.PropertiesChanged(const.INTERFACE, {"mc_version": version},
                                   [])
            print("Installed server")
            return True

    def start(self, timeout):
        """starts the server
        Args:
            timeout (int): seconds before timeout, 0 for no timeout
        Returns:
            bool: true if the server started successfully, false otherwise
        """
        # check that server file exists
        if not (const.SERVER_JAR_PATH.is_file() and
          (const.SERVER_DIR_PATH/self.launch_path).is_file()):
            print("SERVER MUST BE INSTALLED")
            return False
        # check if already running
        if self.status():
            return False        
        # check the ramdisk stopped properly
        if self._world_path.name == const.RAMDISK_PATH.name:
            print("UNGRACEFULL EXIT OCCURED LAST RUN, PLEASE CHECK THE WORLD FILES TO")
            self._world_path = const.SERVER_DIR_PATH / self._config_data["last_world_path"]
            raise IOError("UNGRACEFULL EXIT OCCURED LAST RUN, FILES MAY STILL BE IN RAMDISK\nPLEASE SYNC THE WORLD AND RAMDISK FOLDERS THEN RUN AGAIN")
        else:
            self._config_data["last_world_path"] = self._world_path.name
        # check the eula
        if not self.eula:
            print("You must agree to the eula to launch the server")
            return False
        # check if ramdisk is being used
        if self.ramdisk:
            props = self.server_properties
            props["level-name"] = const.RAMDISK_PATH.name
            self.server_properties = props
            self._ramdisk_graceful_exit = False
            self._ramdisk.load()
        # start the server
        started = self._server_process.start(self.launch_options,
                                             self.launch_path, timeout)
        # if the server started successfully
        if started:
            if self.ramdisk:
                GLib.timeout_add_seconds(interval=self.ramdisk_interval*60,
                                         function=self.ramdisk_save)
            return True
        else:
            return False

    def ramdisk_save(self):
        """saves the ramdisk
        """
        if self.status():
            if self.ramdisk:
                self._ramdisk.save()
                return True
        return False

    def stop(self, timeout):
        """stops the server
        Args:
            timeout (int): seconds before timeout, 0 for no timeout
        Returns:
            bool: true if the server stopped properly, false otherwise
        """
        if not self.status():
            return False
        if self.ramdisk:
            if not self._ramdisk_graceful_exit:
                self._ramdisk.save()
                self._ramdisk_graceful_exit = True
            props = self.server_properties
            props["level-name"] = self._world_path.name
            self.server_properties = props
        return self._server_process.stop(timeout)

    def status(self):
        """returns whether or not the server is running

        Returns:
            bool: true if the server is running, false otherwise
        """
        return self._server_process.status()

    def send(self, command):
        """sends a command to the server

        Args:
            command (str): the command to send tothe server

        Returns:
            bool: True if command was sent
        """
        return self._server_process.send(command)

    def reload_properties(self):
        """tells the server to reload its properties

        Returns:
            bool: True if command was sent
        """
        if self.status():
            return self._server_process.send("reload")
        else:
            return False

    def check_server_state_change(self):
        """checks to see if the server state has changed

        Returns:
            bool: always true to keep loop running
        """
        state = self.status()
        if state != self._server_state:
            self._on_server_state_change(state)
        return True

    def _on_server_state_change(self, newstate):
        """this function sends the server_changed signal when the server
        state changes

        Args:
            newstate (bool): the new state of the server
        """
        if (
            (newstate==False) and
            (not self._ramdisk_graceful_exit)
           ):
            self._ramdisk.save()
            self._ramdisk_graceful_exit = True
        self.server_changed(newstate)
        self._server_state = newstate

    def stop_service(self):
        """quits the loop
        """
        print("service is stopping")
        self.close()
        self._loop.quit()


class server():
    """This class manages , keeps track of, and
    communicates with the minecraft server process.
    """
    def __init__(self):
        self._server = None

    def __del__(self):
        self.stop(120)

    def status(self):
        """returns the server status

        Returns:
            bool: true if server is running
        """
        if self._server is None:
            return False
        return (self._server.poll() is None)

    def stop(self, timeout):
        """Tells the server to shutdown

        Returns:
            bool: true if server process ends within 30 seconds
        """
        if self.send("stop"):
            try:
                self._server.wait(timeout)
            except subprocess.TimeoutExpired:
                self._server.kill()
                return False
        try:
            self._server.stdin.close()
            self._server = None
        except AttributeError:
            return False
        return True

    def start(self, options, path, timeout):
        """starts the minecraft server

        Args:
            options (str): java arguments to use
            path (str): path to the server
        """
        if self.status():
            return False  # return false if already running
        out = const.OUTPUT.open('w')
        arguments = options.copy()
        for i in range(len(arguments)):
            arguments[i] = f"-{arguments[i]}"
        print(f"running \"java -jar {str(' '.join(arguments))} {path}\"\nfrom {str(const.SERVER_DIR_PATH)}")
        self._server = subprocess.Popen(["java", "-jar"] + arguments + [path] +
                                        ["nogui"],
                                        shell=False, stdin=subprocess.PIPE,
                                        stdout=out, bufsize=0,
                                        cwd=const.SERVER_DIR_PATH)

        if self.wait_for(r"\[Server thread/INFO\]: Done"):
                print("Server started!")
                return True
        else:
            return False

    def wait_for(self, message, timeout=30):
        """Waits for a particular regex to appear in the server logs

        Args:
            message (str): a regex to look for in the server's output
            timeout (int, optional): The amount of time to wait before giving up. Defaults to 30.

        Raises:
            TimeoutError: If timeout is reached

        Returns:
            bool: returns if the message was recieved before timeout
        """
        attempt_interval = 0.1
        timer = 0
        log = const.OUTPUT.open('r')
        while True:
            line = log.readline()
            if re.search(message, line):
                return True
            elif timer >= timeout and timeout > 0:
                raise TimeoutError
            else:
                timer += attempt_interval
                sleep(attempt_interval)

    def send(self, command):
        """sends a command to the server's STDIN

        Args:
            command (str): the command to send to the minecraft server

        Returns:
            bool: True if STDIN was written to, false otherwise
        """
        if self._server is None or not self.status():
            return False
        self._server.stdin.write(command.encode()+b"\n")
        print(f"sent command: \"{command}\"")
        return True


class ramdisk():
    """This class is responsible for managing the ramdisk
    """
    def __init__(self, serverobj, path):
        self._server = serverobj
        self._world_path = path

    def save(self):
        """Backs up the contents in the ramdisk folder to the server's world folder
        """
        if self._server.status():
            self._server.send("say server is backing up ramdisk...")
            self._server.send("save-all")
            self._server.wait_for(r"Saved the game", 120)
            self._server.send("save-off")
        sync(const.RAMDISK_PATH, self._world_path, 'sync', create=True, purge=True, verbose=True)
        if self._server.status():
            self._server.send("save-on")
            self._server.send("say server is done backing up ramdisk")

    def load(self):
        """Loads contents from the server's world folder into the ramdisk
        """
        sync(self._world_path, const.RAMDISK_PATH, 'sync', create=True, purge=True, verbose=True)

def start_service():
    """This function starts the mc-as-a-service service
    """
    if not (const.SERVER_DIR_PATH).is_dir():
        const.SERVER_DIR_PATH.mkdir()
    if not const.RAMDISK_PATH.is_dir():
        const.RAMDISK_PATH.mkdir()
    if not const.LOGS_DIR.is_dir():
        const.LOGS_DIR.mkdir()
    service_manager = manager(loop)
    publish = bus.publish(const.INTERFACE, service_manager)
    GLib.timeout_add_seconds(interval=1,
                             function=service_manager.
                             check_server_state_change)
    try:
        loop.run()
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt\nStopping service")
        service_manager.stop_service()
        publish.unpublish()
        print("Exit by Control C")

if __name__ == "__main__":
    start_service()
    
