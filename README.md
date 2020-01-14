
# Auto Updater
Boatswain Auto Updater (BAT) is an open source, multiple platforms auto updater, which will ensure your clients always staying up-to-date with the newest version of your application. Although, BAT is a part of [Boatswain application](https://github.com/theboatswain/boatswain) but we have implemented it separately so that you can easily integrate it with your project, whether or not you are using python or any other languages.



![Boatswain Auto Updater](https://raw.githubusercontent.com/theboatswain/boatswain_updater/master/images/cross-platforms.png)
    
## Build status:  
  
[![Build Status](https://travis-ci.com/theboatswain/boatswain_updater.svg?branch=master)](https://travis-ci.com/theboatswain/boatswain_updater)  
  
## Introduction  
  
Boatswain Auto Updater is a PyQT based, cross-platform application, which allows you to deliver your newest version of your application to your clients. Relying on Github releases web service as backend APIs and hosting storage, you don't need to spend times to build up a Web API or spend a bunch of money to hire any sort of dedicate server for this. The implementation for BAT integration is super easy, just a few lines of code then you are ready to go 🥳

BAT works with or without super user privilege, depending the location of the installation folder. If you installed your application to user directory then the updating process will go smoothly, without asking anything. However, if you installed it into system directory (i.e **Windows**: *C:\Program Files\xxx*, **MacOS**: */Applications/xxx*, **Linux**: */xxx*) then a prompt asking for privilege permission will appear and the user just need to approve it, so then the updater will take care the rest.

## How does it work?
BAT relies on Github releases web services, which mean, you have to declare your Github repo in the implementation (python based) or in the configuration file (non-python based) of your application. Whenever you publish a new release in your Github releases with some **specified release files**, then, in the client side, BAT will notify user and ask for updating. If the user approved, then the following steps will be performed:

 - Download the newly updated version (zip archived) and save into temp folder
 - Extract the downloaded zip file
 - Inside the running application folder, 
	 - Delete all file with ".bak" extension (for cleaning previous version)
	 - Rename all files  by adding *.bak* extension
 - Move everything inside the extracted folder to the running application folder
 - Notify of finishing (python based) or exit (non-python based)

At this step, you will mostly want to restart your application, so then the new update will take effect. But you also can perform some finishing works, depending on your requirements.
### Github release file name's formats
Because of some limitation of Github APIs, we can only use naming convention to specify which release's file for which Operator System and Architecture. In general, your release file name will have the following format:
```bash
<project_name>-(macOS|win-<arch>|linux-<arch>)-<version>.zip
```
Whereas:
 - project_name: Your project's name, can be any characters or numbers ([A-Za-z0-9-_]+)
 - arch: Architecture, value is including 32 or 64, which corresponding to 32-bit and 64-bit architectures
 - version: The new version of your project, have to be using [semver](https://semver.org/) format


## Installation  
### For Python based application
If your project is using python, then add the following lines of code into your main application:
```python
from boatswain_updater.models.feed import Feed  
from boatswain_updater.updater import Updater

feed = Feed('<your github repo>')  #i.e theboatswain/boatswain
pixmap = QIcon(getExternalResource('<Your icon>')).pixmap(QSize(64, 64))  
update_dialog = Updater(None, feed)  
update_dialog.setIcon(pixmap)  
update_dialog.installed.connect(<function to call after finishing updating process>)  
update_dialog.checkForUpdate(silent=True)
```

And also put this line into your *requirements.txt* `boatswain_updater==1.1.3`
You can also take a look at BAT integration [here](https://github.com/theboatswain/boatswain/blob/master/boatswain/main.py#L74-L79) as reference.

### For non-python application
If your project is not using python, or incase you want to make things separately, you can also use the standalone version of Boatswain Auto Updater, which is implemented [here](https://github.com/theboatswain/boatswain_updater/blob/master/boatswain_updater/standalone.py). The prebuilt versions of BAT standalone for each of the platforms can be downloaded from [the releases page](https://github.com/theboatswain/boatswain_updater/releases)

> Alternatively, you can also build BAT standalone from source.

There are two files inside each of the prebuilt releases, including **AutoUpdater** and **update.json**. You should modify the **update.json** file according to your project.

```json
{  
  "Name": "<project_name>",  
  "Version": "<version>",  
  "Icon": "<your_icon>",  
  "Repo": "<your github repo>"  
}
```
Once modified, you can copy these two files into your application's root folder. Now, from your application, you just need to call it to perform the updating procedure.

> Note: For MacOS, you can place the files into *Contents/Resources* folder

For checking new version of your application (in background, for example):

`path/to/AutoUpdater --checking-mode=True`

This command will return to you an output as json format, with the following information:
```json
{
  "has_release": true,
  "last_release": {
    "version": "1.0.0",
    "changelog": "This is the description of this updating",
    "download_url": "https://github.com/theboatswain/updater_example/releases/download/1.0.0/UpdaterExample-macOS-1.0.0.zip",
    "download_size": 25613160
  }
}
```
Although, it will give you a lot of informations regarding your newly version. But you just need to focus on the *"has_release"* attribute. Since it indicates that you have got a new version, and so you can call the AutoUpdater for asking user to update it.

`path/to/AutoUpdater`

This command will launch the Updater dialog and showing the new version to user, asking for updating.

You can see a simple example of how it works in [https://github.com/theboatswain/updater_example](https://github.com/theboatswain/updater_example)
  
## Documentation  
BAT's documentation, user guide and other informations can be found at [https://github.com/theboatswain/boatswain_updater/wiki](https://github.com/theboatswain/boatswain_updater/wiki)  
  
## Building Boatswain  Auto Updater
BAT can be compiled and used on MacOS, Linux and Windows, both 32 bit and 64 bit systems. Tutorial for compiling hasn't finished yet, but you can refer to the one from Boatswain: [installation-mac.md](https://github.com/theboatswain/boatswain/blob/master/installation-mac.md) for MacOS,  [installation-debian.md](https://github.com/theboatswain/boatswain/blob/master/installation-debian.md) for Debian  and [installation-win.md](https://github.com/theboatswain/boatswain/blob/master/installation-win.md)  for Windows.

## Code contributions  
Note: by contributing code to the Boatswain Auto Updater project in any form, including sending a pull request via Github, a code fragment or patch via private email or public discussion groups, you agree to release your code under the terms of the GNU GPLv3 license that you can find in the [LICENSE](https://github.com/theboatswain/boatswain_updater/blob/master/LICENSE)) file included in the Boatswain Auto Updater source distribution.  
  
Please see the [CONTRIBUTING.md](https://github.com/theboatswain/boatswain_updater/blob/master/CONTRIBUTING.md) file in this source distribution for more information.  
  
## Copyright and License  
Code released under the [GNU GPL v3 license](https://github.com/theboatswain/boatswain_updater/blob/master/LICENSE)