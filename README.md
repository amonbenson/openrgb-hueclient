# openrgb-hueclient
Basic Python script for syncing a Philips Hue Room to OpenRGB.

Note that this script is Windows only.

## Setup

### Install Python

You need to install Python 3.9 or higher. You can get the latest Python Version from the [Microsoft Store](https://apps.microsoft.com/detail/9nrwmjp3717k).

### Setup the Script

Open a powershell window and run the setup script:

```powershell
cd C:\path\to\openrgb-hueclient
.\setup.ps1
```

### Obtain a Philips Hue username/hue-application-key

Visit `https://<your-hue-bridge-ip>/debug/clip.html`. Enter the following values:

- URL: `/api`
- Headers: _(leave empty)_
- Message Body:
```json
{
    "devicetype": "openrgb-hueclient#00:00:00:00:00:00",
    "generateclientkey": true
}
```

If you want to, you can replace `openrgb-hueclient#00:00:00:00:00:00` with any other name and your PC's MAC address. Now press the physical Link button on your Hue Bridge and then hit the `POST` button on the website. In the Command Response, you will see something like this:

```json
[
    {
        "success": {
            "username": "<your-username>",
            "clientkey": "<your-client-key>"
        }
    }
]
```

Note down these values, as you will need them in the next step.

### Start the Script

Copy the `.env.example` file to `.env` and fill in `BRIDGE_IP`, `BRIDGE_USERNAME` (from the previous step), and the `BRIDGE_ROOM` you want to sync. If your OpenRGB instance is running on a different PC, you will also need to fill in the `OPENRGB_HOST` and `OPENRGB_PORT` of that PC. Make sure that your Philips Hue Bridge and OpenRGB are running and that the OpenRGB SDK is enabled (`SDK Server` -> `Start Server`). You can now start the script by running:

```powershell
.\run.ps1
```

### Autostart

TODO
