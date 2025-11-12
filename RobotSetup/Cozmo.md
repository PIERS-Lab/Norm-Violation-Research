#  Cozmo
- I higly recommend using linux for this, Ideally WSL if you are using windows, This guide will be going through the linux
 process, There are links to the SDK's documentation included if you want to try setting this up on a different system.
- Some useful links for the Cozmo SDK:
- [Documentation](https://web.archive.org/web/20220715081845/http://cozmosdk.anki.com/docs/)
- [Github](https://github.com/anki/cozmo-python-sdk)

## Enviornment
- Have a virtual enviornment setup with python 3.5.6, later versions have a deprecated async syntax that are neccecary
- also be sure that this enviornment's pip version is 20.3.4, this is the newest that will work with 3.5.
```
pip install --upgrade pip==20.3.3
```
that the Cozmos use, so they won't work on newer python versions.
-If you you haven't done that before, I recommend pyenv, it allows you to manage both virtual enviornments and python versions
###Pyenv
-clone the repository, this command will automatically install with the virtualenv plugin
```
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
```
-Add the following into your bashrc (or equivalent depending on filesystem)
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
 eval "$(pyenv init -)"
fi
```
-Open up a new terminal and check if pyenv is correctly installed
```
pyenv --help
```
-once that is giving an output that's not "command not recognized", install python 3.5 via pyenv
```
pyenv install 3.5
```
-Finally make your enviornment, I have named it "cozmoEnv" but this can be changed if you want
```
pyenv virtualenv 3.5 cozmoEnv
```


## SDK installation

You can find these instructions on the SDK's website on the internet archive, but considering that could 
go down any minute, I am compiling the linux steps here

#### Important!
- You will need to activate your enviornment every time you want to set up anything with the cozmos or run any programs

- if you used pyenv the command will look like this
```
pyenv activate [env]
```

- finally install the SDK itself
```
pip install 'cozmo[camera]'
```

- while you are at it install openGL for the 3d viewer
```
pip install PyOpenGL
```

## Robot Setup
-  An unfortunate property that the cozmos have is that they need to be connected to another device to properly run
-  You can emulate a phone, but this can be slow and emulator quality varies (I recommend android studio if you intend to do this)
-  - For each device you need to download the cozmo app, luckily as of the time of writing this, it is avaliable on both IOS and android.
   - Make sure you get the 3.4 version of the app, as of writing this, the SDK does not support the most recent version yet.
- once this is done, you can follow the in-app instructions to get a cozmo moving, and put it into SDK mode via the in-app settings to run programs
- Now, depending on the OS of the device that you'll be using with the Cozmo,
- you will need either [ADB](https://developer.android.com/tools/adb)(Android) or [usbmuxd](https://web.archive.org/web/20230324060005/https://github.com/libimobiledevice/usbmuxd)
### Android Debug Bridge
- install Android Debug Bridge
  ```
  sudo apt-get install adb
  ```
  -verify
  ```
  adb --version
  ```
  
### Usbmuxd 
- install Android Debug Bridge
```- The instructions for usbmuxd cover the setup needed there
sudo apt-get install usbmuxd
```
-verify
```
usbmuxd --version
```
-if there are any issues, I have linked the websites for both above.
## Running Programs 
clone this repo so that you have the project code there
```
git clone https://github.com/PIERS-Lab/Cozmo-MultiEmbodiment
```
- Once evertyhing is all squared off, run through the following to run programs
- connect to the cozmo with your secondary device and put it into SDK mode
- plug the secondary devices into the computer you'll use to run the programs vis USB
- Verify that the device connection is working if needed (if using adb, just run ``` adb devices ```).
- Then just run the program on the primary device and the robot will properly react. 
