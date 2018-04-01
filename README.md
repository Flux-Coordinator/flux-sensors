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

- add the line `export PATH=~/.local/bin:$PATH` to `~/.bash_profile`
- then run `source ~/.bash_profile` to reload the profile