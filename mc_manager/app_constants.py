from os import environ
from pathlib import Path
import sys

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
            return "mc_manager"

    @property
    def HELP_PATH(self):
        if self.SNAP:
            return Path(environ["SNAP"])/"help.txt"
        else:
            return Path(__file__,'..').resolve()/"help.txt"

    @property
    def MANIFEST_URL(self):
        return "https://launchermeta.mojang.com/mc/game/version_manifest.json"

    @property
    def EULA_URL(self):
        return "https://account.mojang.com/documents/minecraft_eula"
