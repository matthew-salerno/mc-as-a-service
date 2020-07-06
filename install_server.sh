#!/bin/bash
server_jar_path="$2"
manifest_url="https://launchermeta.mojang.com/mc/game/version_manifest.json"

selected_version="$1"
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
if [ ! "$sha1" == "$sha1_server" ]; then
    echo "SHA1 checks do not match, aborting"
    rm -f "$server_jar_path"
    exit 1
fi
echo "SHA1 sums match, installation complete"
exit 0
