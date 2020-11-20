# Muonic 4
[![Documentation Status](https://readthedocs.org/projects/muonic/badge/?version=latest)](https://muonic.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![CI](https://github.com/NetzwerkTeilchenwelt/muonic4/workflows/CI/badge.svg)
[![Coverage Status](https://coveralls.io/repos/github/NetzwerkTeilchenwelt/muonic4/badge.svg?branch=master)](https://coveralls.io/github/NetzwerkTeilchenwelt/muonic4?branch=master)

Rewrite of the Netzwerkteilchenwelt Muonic Software.
Sill in very early development.

### Code organization 
The source code of muonic 4 currently (!!!) lives in the "rewrite" directory. All pull requests should reference this directory.

## Documentation
More documentation can be found [here](https://muonic.readthedocs.io/en/latest/)

## Prequisites

```bash
pip install -r requirements.txt
```

## Running muonic
Currently the headless (no gui) version of muonic can take rate measurements. In order to run a rate measurement attach a DAQ card, then open a terminal in the rewrite diirectory and run: 
```bash
python3 runServer.py
```

keep this terminal open, open a second one and run: 

```bash
python3 runRates.py
```




## To do in Repo Setup

- :white_check_mark: Auto-documentation via Sphinx
- :white_check_mark: Webhook to readthedocs
- :white_check_mark: Auto pep-8 (or other code formatter)
- [ ] Unittests
- [ ] Webhooks to Dockerhub
- [ ] Webhooks to pip?
- [ ] Github CI Action or travis.ci ???
- [ ] Code coverage
- :small_red_triangle: Github Superlinter (disabled for now as it is way to harsh on existing code)

## Todo for the Software
- :white_check_mark: Port the headless version
- :white_check_mark: Implement socket communication
- :white_check_mark: Convert Muonic to Python3
- [ ] Port the existing analysis' to the new version
