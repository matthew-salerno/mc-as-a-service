#!/bin/bash
bash "$SNAP""/bin/header.sh"

#EULA FUNCTION
##EULA
function eula () {
    echo "Eula path: \"""$eula_path""\""
    echo "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula)." > "$eula_path"
    echo "#""`date`" >> "$eula_path"
    if (whiptail --title "EULA" --yesno --scrolltext "YOU MUST AGREE TO THE EULA TO RUN A MINECRAFT SERVER\nPlease read the EULA in its entirety, selecting yes indicates that you agree to the EULA:\n\n""`lynx --cfg "$SNAP""/etc/lynx/lynx.cfg" --dump --anonymous "https://account.mojang.com/documents/minecraft_eula" | sed '/^ *\*\|^ *+/d' | sed '1,+4d'`" 30 78); then
        echo "eula=true" >> "$eula_path"
        return 0
    else
        echo "eula=false" >> "$eula_path"
        return 1
        whiptail --title "EULA" --msgbox "You must agree to the EULA to to use this software" 30 78
    fi
}

##ignore eula if it is already filled out
#eula starts out as false
eula="0"
if [ -f "$eula_path" ]; then
    if [[ `cat "$eula_path" | grep "eula="` =~ .*true ]]; then
        eula="1"
    fi
fi

if [ $eula = "0" ]; then
    eula
    if [[ $? = 1 ]]; then
        exit 0
    fi
fi

#get preferred release
ADVSEL=$(whiptail --title "Installer" --menu --nocancel "Please choose a minecraft version" 30 78 4 \
    "1" "Release" \
    "2" "Snapshot" 3>&1 1>&2 2>&3)
case $ADVSEL in
    1)
        BRANCH="release"
    ;;
    2)
        BRANCH="snapshot"
    ;;
esac

if (whiptail --title "Installer" --yesno "Would you like to download the latest server?" 30 78); then
    download_latest="true"
else
    download_latest="false"
fi

selected_version=""
if [ "$download_latest" = "false" ]; then
    versions_menu=()
    if [ "$BRANCH" = "release" ]; then
        versions=($(curl -fsL "$manifest_url" | jq -r '.versions | map(select(.type == "release")) | map(.id) | @sh'))
        for version in ${versions[@]}
        do
            versions_menu+=($version)
            versions_menu+=("''")
        done
    else
        versions=($(curl -fsL "$manifest_url" | jq -r '.versions | map(select(.type == "snapshot")) | map(.id) | @sh'))
        versions_menu=()
        for version in ${versions[@]}
        do
            versions_menu+=($version)
            versions_menu+=("''")
        done
    fi
    selected_version=$(whiptail --title "Installer" --noitem --nocancel --menu "Please choose a minecraft version" 30 78 20 ${versions_menu[@]} 3>&1 1>&2 2>&3 | sed "s/^'//" | sed "s/'$//")
else
    if [ "$BRANCH" = "release" ]; then
        selected_version=$(curl -fsL "$manifest_url" | jq -r '.latest.release | @sh' | sed "s/^'//" | sed "s/'$//")
    else
        selected_version=$(curl -fsL "$manifest_url" | jq -r '.latest.snapshot | @sh' | sed "s/^'//" | sed "s/'$//")
    fi
fi

#get the url for the package json
echo "Seected version: "$selected_version""
version_package_url=$(curl -fsL "$manifest_url" | jq -r '.versions | map(select(.id == "'$selected_version'")) | map(.url) | @sh' | sed "s/^'//" | sed "s/'$//")
echo "Found version package at "$version_package_url""
#get download location from package json
download_location=$(curl -fsL "$version_package_url" | jq -r '.downloads.server.url | @sh' | sed "s/^'//" | sed "s/'$//")
echo "Downloading from "$download_location""
#download the server
curl -fLso "$server_jar_path" "$download_location"
echo "Download complete"

#check sha1
sha1=`curl -fsL "$version_package_url" | jq -r '.downloads.server.sha1 | @sh' | sed "s/^'//" | sed "s/'$//"`
echo "SHA1 in version package: "$sha1""
sha1_server=`sha1sum $server_jar_path | sed 's/ .*//'`
echo "SHA1SUM for "$server_jar_path":  "$sha1_server""
if [ ! "$sha1" = "$sha1_server" ]; then
    echo "SHA1 checks do not match, aborting"
    rm -f "$server_jar_path"
    exit 1
fi
echo "SHA1 sums match, installation complete"
exit 0
