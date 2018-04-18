# FLUX-Sensors
FLUX-Sensors collects and combines positioning and illuminance data. It is running on the Raspberry Pi and forwards all data to an http server.
## Requirements

- Python 3
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