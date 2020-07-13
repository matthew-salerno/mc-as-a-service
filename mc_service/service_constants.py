from os import environ
from pathlib import Path
if "SNAP" in environ:
    from pydbus import SystemBus as UsedBus
else:
    from pydbus import SessionBus as UsedBus
class constants():
    @property
    def SNAP(self):
        if "SNAP" in environ:
            return True
        else:
            return False

    @property
    def INTERFACE(self):
        return "com.salernosection.mc_as_a_service.manager"

    @property
    def VERSION(self):
        if self.SNAP:
            return environ["SNAP_VERSION"]
        else:
            return "unknown"

    @property
    def NAME(self):
        if self.SNAP:
            return environ["SNAP_NAME"]
        else:
            return "mc_service"

    @property
    def ROOT_PATH(self):
        if self.SNAP:
            return Path(environ["SNAP_COMMON"])
        else:
            return Path(__file__,'..').resolve()

    @property
    def SERVER_DIR_PATH(self):
        return self.ROOT_PATH/"server"

    @property
    def SERVER_JAR_PATH(self):
        return self.SERVER_DIR_PATH/"server.jar"

    @property
    def EULA_PATH(self):
        return self.SERVER_DIR_PATH/"eula.txt"

    @property
    def CONFIG_PATH(self):
        return self.ROOT_PATH/"config.json"

    @property
    def RESOURCES_DIR(self):
        if self.SNAP:
            return Path(environ["SNAP"])/"resources"
        else:
            return self.ROOT_PATH/"resources"

    @property
    def DEFAULT_CONFIG_PATH(self):
        if self.SNAP:
            return self.RESOURCES_DIR/"default_config.json"
        else:
            return self.RESOURCES_DIR/"default_config.json"

    @property
    def PROPERTIES_PATH(self):
        return self.SERVER_DIR_PATH/"server.properties"

    @property
    def LOGS_DIR(self):
        return self.ROOT_PATH/"logs"

    @property
    def OUTPUT(self):
        return self.LOGS_DIR/"out.log"

    @property
    def RAMDISK_PATH(self):
        return self.SERVER_DIR_PATH/"ramdisk"

    @property
    def XML_PATH(self):
        return self.RESOURCES_DIR/"interface.xml"

    @property
    def MANIFEST_URL(self):
        return "https://launchermeta.mojang.com/mc/game/version_manifest.json"
    
    @property
    def BUS(self):
        return UsedBus()