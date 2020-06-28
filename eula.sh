#!/bin/bash
manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"
config_path="$SNAP""/etc/mc-as-a-service.json"
server_path="$SNAP""`cat "$config_path" | jq -r '.launcher.server_path | @sh' | sed "s/^'//" | sed "s/'$//"`"
eula_path=$server_path"/eula.txt"
##EULA
echo "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula)." > $eula_path
echo "#""`date`" >> $eula_path
echo "`lynx --cfg "$SNAP""/etc/lynx/lynx.cfg" --dump --anonymous "https://account.mojang.com/documents/minecraft_eula" | sed '/^ *\*\|^ *+/d' | sed '1,+2d'`"
if (whiptail --title "EULA" --yesno --scrolltext "YOU MUST AGREE TO THE EULA TO RUN A MINECRAFT SERVER\nPlease read the EULA in its entirety, selecting yes indicates that you agree to the EULA:\n\n""`lynx --cfg "$SNAP""/etc/lynx/lynx.cfg" --dump --anonymous "https://account.mojang.com/documents/minecraft_eula" | sed '/^ *\*\|^ *+/d' | sed '1,+2d'`" 30 78); then
    echo "eula=true" >> $eula_path
    echo "set eula to true"
else
    echo "eula=false" >> $eula_path
    echo "set eula to false"
    whiptail --title "EULA" --msgbox "You must agree to the EULA to to use this software" 30 78
fi
