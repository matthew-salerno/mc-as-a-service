#!/bin/bash
eula_path="$1"
echo "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula)." > "$eula_path"
echo "#""`date`" >> "$eula_path"
if (whiptail --title "EULA" --yesno --scrolltext "YOU MUST AGREE TO THE EULA TO RUN A MINECRAFT SERVER\nPlease read the EULA in its entirety, selecting yes indicates that you agree to the EULA:\n\n""`lynx --cfg "$SNAP""/etc/lynx/lynx.cfg" --dump --anonymous "https://account.mojang.com/documents/minecraft_eula" | sed '/^ *\*\|^ *+/d' | sed '1,+4d'`" 30 78); then
    echo "eula=true" >> "$eula_path"
    exit 0
else
    echo "eula=false" >> "$eula_path"
    exit 1
    whiptail --title "EULA" --msgbox "You must agree to the EULA to to use this software" 30 78
fi