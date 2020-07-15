# mc-as-a-service
Runs a minecraft server as a system service in the background

## USAGE
### Commands
Once the service is running (see *installation*), you can control the
service with the mc-manager command. This can operate as a command line
interface or through the TUI. To use the TUI, just enter ```mc-manager```
with no arguments.
The arguments for ```mc-manager``` are as follows:  
| command           | description                    | example |
|:------------------|:------------------------------:|:--------|
|```start```        | Starts the minecraft server|```mc-manager start```|
|```stop```         | Stops the minecraft server|```mc-manager stop```|
|```send server_command...```         | sends a command to the server|```mc-manager send say hello world```|
|```status```| Returns the status of the minecraft server (running or not) |```mc-manager status```|
|```connect```\*| Enters the minecraft console|```mc-manager connect```|
|```get-eula```| Returns whether or not the user has agreed to the minecraft EULA |```mc-manager get-eula```|
|```eula```| Shows user the minecraft EULA and signs it if the user agrees |```mc-manager eula```|
|```install [version]```| Installs the specified minecraft version if given, otherwise the version will be selected through the TUI | ```mc-manager install 1.16.1```|
|```launch-path [path]```| Returns the path of the jarfile run by java, relative to the server directory. If a path is given, it changes java to launch the given path|```mc-manager launch-path fabric-server-launch.jar```|
|```launch_options [options...]```| Specifies java options to use | ```mc-manager launch-options Xmx2G Xms1G```|
|```set-property key [value]``` Deletes a property (returns to default) when just the key is specified, otherwise sets the property to value | ```mc-manager set-property enable-rcon true``` |
|```ramdisk [value]```\*\*| Returns if the ramdisk is being used if no option is given, otherwise turns on/off the ramdisk according to the option | ```mc-manager ramdisk true```|
|```ramdisk-interval time```\*| Sets the time, in minutes, between the ramdisk backing up to the main level folder | ```mc-manager ramdisk-interval 30```|
|```service-stop``` | Tells the daemon to shut down|```mc-manager stop-service```|  

\* Not yet implemented  
\*\* Read the section on ramdisks first! Not knowing what this does can cause wear on your drive at no benefit.
### The ramdisk
All the ramdisk feature does is create a folder named ramdisk in the server directory. server.properties is told to use the level *ramdisk* when it starts and is set back to the original level-name after the server shuts down. **This means you must mount your own ramdisk to the empty server/ramdisk folder before using this feature**. This can be done with makefs or preferrably fstab to create a tmpfs or ramfs filesystem and mount it to that location.  
Should your server stop unexpectadly, the ramdisk may not have backed up to your world folder. If the service detects this, it will not start on the first attempt and will print a message to the service log, *you will only see that the server failed to start from the app side*. You may still have your files in the ramdisk folder if your system did not power off, you can sudo into it to recover the files. Whenever you are ready, run the start command again. The service will ignore the error on the second attempt.
## INSTALLATION
**Currently not released, this will not work**
  
first download the snap with:  
```sudo snap install mc-as-a-service```  
  
A connection must be made between the service and user app:  
```sudo snap connect mc-as-a-service:dbus-plug mc-as-a-service:dbus-slot```
  

From there you can manage the service with the normal snap service commands:
```
sudo snap start mc-service  
sudo snap stop mc-service
sudo snap logs mc-service
etc...
```  

To use control the service, use the mc-manager app described in the *usage* section.
