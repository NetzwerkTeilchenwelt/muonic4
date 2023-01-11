# Muonic 4
[![Documentation Status](https://readthedocs.org/projects/muonic/badge/?version=latest)](https://muonic.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![CI](https://github.com/NetzwerkTeilchenwelt/muonic4/workflows/CI/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/NetzwerkTeilchenwelt/muonic4/badge.svg?branch=master)](https://coveralls.io/github/NetzwerkTeilchenwelt/muonic4?branch=master)

Rewrite of the Netzwerkteilchenwelt Muonic Software.

### Code organization
The source code of muonic 4 currently (!!!) lives in the "rewrite" directory. All pull requests should reference this directory.

## Documentation
More documentation can be found [here](https://muonic.readthedocs.io/en/latest/)

## Permissions
To access the DAQ-card (```/dev/ttyUSB0```), the permissions have to be set correctly. Usually,
it's enough to ensure the user is in the group dialout (edit ```/etc/group```). 

## Docker
Muonic provides a Docker container, which comes with all dependencies. This is the preferred method of running muonic. 
You might need to install docker on the system beforehand:
```bash
sudo apt-get install docker.io
```

Ensure the user is in the group 'docker' (edit ```/etc/group``` and re-login).
There is a ```runDocker.sh``` script, which builds the Docker container - if necessary - and starts the GUI.

## Running without Docker
It is possible to run muonic4 without docker. On current systems it won't work, though. 
Running without docker in production however is highly discuraged. 
Continue at your own risk.
### Prequisites

```bash
pip3 install -r requirements.txt
```

Please also make sure to install the pyqt packages for your distribution. For Ubuntu they can be installed via:
```bash
sudo apt install -y python3-pip libgl1 libglib2.0-0 python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools
```

### Running muonic
Currently the headless (no gui) version of muonic can take rate measurements. In order to run a rate measurement attach a DAQ card, then open a terminal in the rewrite directory and run:
```bash
python3 runServer.py
```

keep this terminal open, open a second one and run:

```bash
python3 runRates.py
```

## GUI
Muonic provides a GUI written in PyQt5. The GUI can be started by running:
```bash
python3 runGUI.py
```
in the rewrite directory.

## Running on Mac and/or Docker

Basically follow this link to setup a GUI on macOS (https://affolter.net/running-a-docker-container-with-gui-on-mac-os/)[https://affolter.net/running-a-docker-container-with-gui-on-mac-os/]. The steps are listed below

### Install dependencies
- `brew install --cask docker`
- `brew install xquartz`
- Open XQuartz and in settings open the security tab. Here allow connections from network clients.
- `./runDocker.sh`

## Troubleshooting
### macOS permissions
If you get an error on macOS stating something about permission denied, when running the `runDocker.sh` script, please try:
```bash
xattr -r -d com.apple.quarantine runDocker.sh
```
### Empty Queue
If muonic misbehaves for any reason ("Port cannot be opened", "Queue is empty"), it is a good measure to stop all running muonic instances by running:
```bash
killall python3
```
If that does not help, one can also press the "BOARD RESET" button on the DAQ card. It is important to wait for about 15 seconds after pressing the reset button, as the board needs some time to be up and running again.

If you are running in docker you can kill the program by running
```bash
docker ps
```

This will yield an output like this:
```bash
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS          PORTS     NAMES
ba1d3ae70903   muonic    "python3 /app/rewrit…"   13 minutes ago   Up 13 minutes             heuristic_meninsky
```

Copy the ID from the first column and run:
```bash
docker kill ba1d3ae70903
```
This kills the container.

## To do in Repo Setup

- :white_check_mark: Auto-documentation via Sphinx
- :white_check_mark: Webhook to readthedocs
- :white_check_mark: Auto pep-8 (or other code formatter)
- :white_check_mark: Unittests
- [ ] Webhooks to Dockerhub
- [ ] Webhooks to pip?
- :white_check_mark: Github CI Action or travis.ci ???
- :white_check_mark: Code coverage
- :small_red_triangle: Github Superlinter (disabled for now as it is way to harsh on existing code)

## Todo for the Software
- :white_check_mark: Port the headless version
- :white_check_mark: Implement socket communication
- :white_check_mark: Convert Muonic to Python3
- :white_check_mark: Port the existing analysis' to the new version
