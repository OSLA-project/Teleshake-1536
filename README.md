[![Python application](https://github.com/OSLA-project/Teleshake-1536/actions/workflows/python-app.yml/badge.svg)](https://github.com/OSLA-project/Teleshake-1536/actions/workflows/python-app.yml)
# Teleshake 1536 SiLA2 Driver
This repository contains a SiLA2 driver for the Teleshake 1536 microplate shaker. It has been forked from 
[the original](https://gitlab.com/sila-driver-group/teleshake) and functionality has been extended to support multiple
attached shakers.

## Getting started

### Prerequisites:

- Python 3.12 or later

### Install and run driver

```shell
# Install package
pip install .

# Start driver on port 50050
python -m sila2_driver.thermoscientific.teleshake1536 --port 50050
```

### Connect to the SiLA server
You can use the [SiLA Browser](https://gitlab.com/unitelabs/sila2/sila-browser) to test the service. 

### Quick docker run
This repository contains a dockerfile and docker-compose file to quickly test the driver in a docker container and view
it in the SiLA browser. To run this, make sure you have installed [docker engine](https://docs.docker.com/engine/install/) or
[desktop](https://docs.docker.com/desktop/) and run the following command:

```shell
docker compose up
````

### Development install
[uv](https://docs.astral.sh/uv/) is used for dependency and environment management. In order to install the drivers and
set up your python environment, run the following in the root of the repository:

```shell
uv sync
```

This project uses a pre-commit hook to check code formatting and linting. To set up the pre-commit hook, run:

```shell
uv run pre-commit install
```