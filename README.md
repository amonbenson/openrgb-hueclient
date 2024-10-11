# openrgb-hueclient
Basic Python script for syncing your PC's RGB lighting with your Philips Hue lights.

Note that this script is Windows only.

## Prerequisites

### Setup OpenRGB

You need to install OpenRGB. You can get the latest version from [here](https://openrgb.org/releases.html).

You also need to make a few adjustments to the OpenRGB settings:
- Navigate to `Settings` > `General` and enable `Start At Login`, `Start Minimized`, and `Start Server`.
- Navigate to `Settings` > `Plugins` and disable the `OpenRGB Effects Plugin` (if installed).
- Navigate to `SDK Server` and click `Start Server`.

### Setup Python

You need to install Python 3.9 or higher. You can get the latest Python Version from the [Microsoft Store](https://apps.microsoft.com/detail/9nrwmjp3717k).

## Install

Open a powershell window and run following commands:

```powershell
cd C:\path\to\openrgb-hueclient
.\scripts\install.ps1
```

This will:
- Setup a python virtual environment at `.venv`
- Install all required python packages
- Connect to your Hue Bridge and ask you to press the button on the bridge
- Connect to OpenRGB
- Store all credentials in a file called `.env`
- Register a scheduled task that runs the script when you log in
- Start the script

If everything worked, you should now see the lights on your PC change colors to match your selected Hue Room.

## Uninstall

Open a powershell window and run following commands:

```powershell
cd C:\path\to\openrgb-hueclient
.\scripts\uninstall.ps1
```

This will:
- Stop the script if it is running
- Remove the scheduled task

The virtual environment and `.env` file will stay in place. If you want to completely reset the application, you can delete the `.venv` folder and the `.env` file. Note that you will need to pair with the Hue Bridge again if you do this.
