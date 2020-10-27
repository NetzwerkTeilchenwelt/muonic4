# Muonic 4
[![Documentation Status](https://readthedocs.org/projects/muonic/badge/?version=latest)](https://muonic.readthedocs.io/en/latest/?badge=latest)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
![CI](https://github.com/NetzwerkTeilchenwelt/muonic4/workflows/CI/badge.svg)

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
