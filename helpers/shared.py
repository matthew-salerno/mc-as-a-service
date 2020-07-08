from os import environ
from pathlib import Path


class constants():
    @property
    def INTERFACE(self):
        return "com.salernosection.mc_as_a_service.manager"

    @property
    def VERSION(self):
        if "SNAP" in environ:
            return environ["SNAP_VERSION"]
        else:
            return "unknown"

    @property
    def NAME(self):
        if "SNAP" in environ:
            return environ["SNAP_NAME"]
        else:
            return "app.py"

    @property
    def ROOT_PATH(self):
        if "SNAP" in environ:
            return Path(environ["SNAP_COMMON"])
        else:
            return Path(__file__,'..','..').resolve()
    @property
    def SERVICES_PATH(self):
        if "SNAP" in environ:
            return Path(environ["SNAP"]/"services")
        else:
            return self.ROOT_PATH/"services"

    @property
    def APPS_PATH(self):
        if "SNAP" in environ:
            return Path(environ["SNAP"]/"apps")
        else:
            return self.ROOT_PATH/"apps"

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
    def PROPERTIES_PATH(self):
        return self.SERVER_DIR_PATH/"server.properties"

    @property
    def OUTPUT(self):
        return self.ROOT_PATH/"out.log"

    @property
    def RAMDISK_PATH(self):
        return self.SERVER_DIR_PATH/"ramdisk"

    @property
    def RAMDISK_TEMP_PATH(self):
        return self.SERVER_DIR_PATH/".temp_ramdisk"

    @property
    def XML_PATH(self):
        return self.SERVICES_PATH/"interface.xml"

    @property
    def MANIFEST_URL(self):
        return "https://launchermeta.mojang.com/mc/game/version_manifest.json"

    @property
    def EULA_URL(self):
        return "https://account.mojang.com/documents/minecraft_eula"
