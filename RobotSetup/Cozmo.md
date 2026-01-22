#  Cozmo
- I highly recommend using linux for this, Ideally WSL if you are using windows, This guide will be going through the linux
 process, There are links to the SDK's documentation included if you want to try setting this up on a different system.
- Some useful links for the Cozmo SDK:
- [Documentation](https://web.archive.org/web/20220715081845/http://cozmosdk.anki.com/docs/)
- [Github](https://github.com/anki/cozmo-python-sdk)

## Enviornment
- Have a virtual enviornment setup with python 3.5.6, newer versions have a deprecated async syntax that are neccecary for Cozmo's SDK to work.

- If you you haven't done that before, I recommend pyenv, it allows you to manage both virtual enviornments and python versions fairly easily.

### Pyenv
- Grab the build essantials
```
sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev curl git libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```
- Install pyenv
```
curl -fsSL https://pyenv.run | bash
```
- Clone the repository for the virtualenv plugin, the second part of the command places the plugin where it should be.
```
git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
```
- Add the following into your bashrc
```
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if command -v pyenv 1>/dev/null 2>&1; then
 eval "$(pyenv init -)"
fi
```
- Open up a new terminal and check if pyenv is correctly installed.
```
pyenv --version
```
- Once that is giving an output that's not "command not recognized", install python 3.5 via pyenv.
```
pyenv install 3.5
```
- Finally make your enviornment, I have it named "cozmoEnv" here but this can be what ever you want. 
```
pyenv virtualenv 3.5 cozmoEnv
```
- Also be sure that this enviornment's pip version is 20.3.3, this is the newest that will work with 3.5, this is not necceary but it will give you the best versions of libraries associated with that python version.

```
pip install --upgrade pip==20.3.3
```

## SDK installation

You can find these instructions on the SDK's website on the internet archive, but considering that could 
go down any minute, I am compiling the linux steps here

#### Important!
- You will need to activate your enviornment every time you want to set up anything with the cozmos or run any programs
```
pyenv activate [env]
```

- Install the SDK itself.
```
pip install 'cozmo[camera]'
```

- While you are at it install openGL for the 3d viewer.
```
pip install PyOpenGL
```

- Install the needed libraries for apriltag use.
```
pip install apriltag
```
and
```
pip install numpy
```

- Finally, install matplotlib for visualization
```
pip install matplotlib
```

## Robot Setup
-  An unfortunate property that the cozmos have is that they need to be connected to another device to properly run.
-  You can emulate a phone, but this can be slow and emulator quality varies and you will need one that can handle connecting to a network on it's own. this is hard to do and it will generally be easier to just use a physical device.
### Cozmo app
- For each device you need to download the cozmo app, while this does cost money now, this version of the program uses an older version (3.4.3).

  - Cozmo's firmware directly pairs with the app, so you will need to to factory reset cozmo to ensure this.
    - Place Cozmo onto the charger, and ehile holding the backpack button raise and drop his lifter three times, it'll take asecond after, but cozmo will breifly shut off and turn back on.
    - Finally just connect to cozmo's wifi and launch the app, the app will then install the matching firmware onto the robot!
- Note that getting the app is an annoying task, if you are on andoid you can get an APK (I use APK pure to make this easier) to get the right version, I have not been able to verify a way to get this done on IOS, though.

- Once this is done, you can follow the in-app instructions to get Cozmo moving, and put it into SDK mode via the in-app settings to run programs.

### Putting Cozmo into SDK Mode

  - Connect to cozmo's wifi on the device that you set the app up on. If you need the network password, put cozmo on the charger and move the lifter up and down, this will display it. Once cozmo has activated, click the top right icon (It'll look like 3 small sliders in a box) and scroll to the right until you find the enable SDK button, hit it and you are good to go!



- Now, depending on the OS of the device that you'll be using with the Cozmo, you will need either [ADB](https://developer.android.com/tools/adb)(Android) or [usbmuxd](https://web.archive.org/web/20230324060005/https://github.com/libimobiledevice/usbmuxd)(IOS)
### Android Debug Bridge
- Install Android Debug Bridge
  ```
  sudo apt-get install adb
  ```
  -Verify
  ```
  adb --version
  ```
  
### Usbmuxd 
- Install Usbmuxd
```
sudo apt-get install usbmuxd
```
- Verify
```
usbmuxd --version
```
- If there are any issues, I have linked the websites for both above.

## Running Programs 
Clone this repo so that you have the project code on your machine.
```
git clone https://github.com/PIERS-Lab/Norm_Violation_Research
```
- Once evertyhing is all squared off, run through the following to run programs
- Connect to the cozmo with your secondary device and put it into SDK mode.
- Plug the secondary devices into the computer you'll use to run the programs.
  - For some explanation, The SDK works by using the main computer to send commands to the devices connceted to cozmo, which then relays the commands to the robot to be properly executed.
- Verify that the device connection is working if needed (if using adb, just run ``` adb devices ```).
- Then just run the program on the primary device and the robot will properly react.

# Common Issues

- If you have your device plugged in with Cozmo running and the program is reprting that here are no devices runnig Cozmo, make sure your USB cable can handle data transfer. Also on that issue, sometimes Cozmo will auto sleep if idle for too long, so check that the device is still connected and that cozmo has enough charge left (you can tell by the colors on the backpack light).

- If you are using an android, make sure that your device is in developer mode, otherwise the SDK will not be able to relay commands.

- If you start getting version mismatch issues, your app may have auto updated and you will need to downgrade it to the correct version. This can also happen the other way where cozmo may already have the newest firmware installed, in any case, refer back to the cozmo app section of this read me to fix it.

