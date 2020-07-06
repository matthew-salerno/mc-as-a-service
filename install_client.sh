#!/bin/bash
manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"

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
            versions_menu+=("''") #fill with empty line because whiptail needs two values for every option
        done
    else
        versions=($(curl -fsL "$manifest_url" | jq -r '.versions | map(select(.type == "snapshot")) | map(.id) | @sh'))
        versions_menu=()
        for version in ${versions[@]}
        do
            versions_menu+=($version)
            versions_menu+=("''") #fill with empty line because whiptail needs two values for every option
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

#return the version for the server to install
echo $selected_version
