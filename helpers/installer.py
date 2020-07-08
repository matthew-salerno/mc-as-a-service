if __name__ == "__main__":
    import shared
else:
    from helpers import shared
import urllib3
import json
import hashlib
from pathlib import Path
const = shared.constants()
https = urllib3.PoolManager()
def install_server(version):
    manifest = json.loads(https.request('GET',const.MANIFEST_URL).data.decode("utf-8"))
    if version == "release" or version == "snapshot":
        version = manifest["latest"][version]
    packages    = list(filter(lambda ver: ver["id"] == version, manifest["versions"]))
    if not len(packages):
        print(f"Could not find server matching \"{version}\"")
        return None
    package_url  = packages[0]["url"]
    package = json.loads(https.request('GET',package_url).data.decode("utf-8"))
    sha1_https =  package["downloads"]["server"]["sha1"]
    server_url = package["downloads"]["server"]["url"]
    server_jar = download(server_url, const.SERVER_JAR_PATH, sha1_https)
    return server_jar

# TODO
def download(url, path, sha1_https=None):
    url_stream = https.request('GET', url, preload_content=False)
    sha1_file = hashlib.sha1()
    print(f"Downloading from {url}")
    with path.open('wb') as out:
        while True:
            data = url_stream.read(2**16)
            if not data:
                break
            sha1_file.update(data)
            out.write(data)
        out.close()
    url_stream.release_conn()
    if sha1_https is not None:
        print("Download complete, checking sha1")
        sha1_local = sha1_file.hexdigest()
        print(f"SHA1 of file:  {sha1_local}")
        print(f"SHA1 provided: {sha1_https}")
        if sha1_https == sha1_local:
            print("Checks passed\nDone")
            return path
        else:
            print("Checks did not pass, deleting file...")
            path.unlink()
            print("Removed file")
            return None
    else:
        print("Download complete, no sha1 provided, could not verify")
        return path

if __name__ == "__main__":
    install_server("1.16.1")