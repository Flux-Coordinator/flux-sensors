# FLUX-Sensors
FLUX-Sensors collects and combines positioning and illuminance data. It is running on the Raspberry Pi and forwards all data to an http server.
## Requirements

- Python 3.5
- Pip
- Virtualenv: `pip3 install virtualenv`

## Run development environment
Start virtualenv to create an isolated Python environment:

```
cd flux-sensors
virtualenv -p <path/to/python3> venv
source venv/bin/activate
pip3 install --editable .
```
The cli command `flux` should be available now inside the virtual environment.

Stop virtualenv when finished: `deactivate`

## Install productive
```
cd flux-sensors
pip3 install .
```
The cli command `flux` should be available now.

If the command is not found, `~/.local/bin/` has to be added to the `$PATH`:

- add the line `export PATH=~/.local/bin:$PATH` to `~/.bash_profile`:
 `echo 'export PATH=~/.local/bin:$PATH' >>~/.bash_profile`
- then run `source ~/.bash_profile` to reload the profile

## Install as a service at startup
Create a systemd unit file called flux.service:
```
sudo nano /lib/systemd/system/flux.service
```
Add the following content:
```
[Unit]
Description=FluxSensors
After=multi-user.target

[Service]
Type=idle
User=pi
ExecStart=/usr/bin/python3.5 -u /home/pi/flux-sensors/flux_sensors/__main__.py 

[Install]
WantedBy=multi-user.target
```
Note that the paths are absolute and fully define the location of the installed Python and the cloned Flux-sensors repository.

Then the permission on the unit file needs to be set to 644:
```
sudo chmod 644 /lib/systemd/system/flux.service
```
Now configure systemd to start the service during the boot sequence:
```
sudo systemctl daemon-reload
sudo systemctl enable flux.service
```
After a reboot the service will start automatically.

The status of the service can be checked using:
```
sudo systemctl status flux.service
```
To view the logs use journalctl:
```
journalctl -u flux.service --follow
```

## Connect the light sensor
This project is tested with the [TCS3430](http://ams.com/eng/Products/Light-Sensors/Color-Sensors/TCS3430) light sensor from AMS. Connect the sensor according to the following mapping scheme:

| Raspberry GPIO | Light Sensor |
|----------------|--------------|
| Pin 1: 3.3V    | Pin 2 3V0    |
| Pin 3: SDA     | Pin 4 SDA    |
| Pin 5: SCL     | Pin 5 SCL    |
| Pin 6: GND     | Pin 3 GND    |

Check the setup by printing a list of all available I2C-devices:

```
i2cdetect -y 1
```

The I2C-address of this sensor should be 0x39.

## Configure the server connections
Crete a config file called flux-config.ini at /home/pi/.config:
```
sudo nano /home/pi/.config/flux-config.ini
``` 
Add the following content:
```
[Flux Server URLs]
LAN=http://192.168.1.104:9000
CLOUD=https://flux-server-staging.herokuapp.com
LOCAL=http://localhost:9000

[Flux Server Connection Settings]
timeout=5
```
The names of the urls can be chosen freely. The script will go through the urls from top to bottom until it gets an answer.

The timeout defines the maximum time to try connecting a url. It is set in whole seconds.