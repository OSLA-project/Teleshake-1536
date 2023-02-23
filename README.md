# SiLA Library

Library of SiLA2 drivers for laboratory automation

## Getting started

### Prerequisites: 

* Python 3.9 or later 
* SiLA client - you can find an open source client here [Universal SiLA Client](https://gitlab.com/SiLA2/universal-sila-client/sila_universal_client )
Note: if you are usuning the Universal Sila Client you will need [java 17](https://www.oracle.com/java/technologies/downloads/#jdk17-windows )

### Folder structure

Each driver follows the following folder structure:

```
root/
├─── docs
│   └── (any driver relevant documentation goes here)
├── pyproject.toml
├── README.md
├── requirements.txt
├── feature_xml
│   ├── *.sila.xml
├── src
│   └── sila2
│       └── driver
│           └── manufacturer
│               └── device_name
│                   └── feature_implementations
│                   └── generated
│                   └── server.py
│                   └── ...
└── tests
```

### Naming

The name of the SiLA server module should follow the following structure:
`sila2-drv-<device_type>-<manufacturer>-<device_name>`

Note: the information to name the device might not always be available and in some cases to remove some of it might make more sense. The above should be followed to the extent possible and servers should be treated case by case.

Example:  `sila2-drv-shaker-thermoscientific-teleshake1536`

### Install and run driver

```shell
# Setup and activate virtual environment
python -m venv venv
./venv/Scripts/activate

# Install package dependencies
python -m pip install -r requirements.txt

# Generate required SiLA2 boilerplate
codegen.bat

# Install package
python -m pip install .

# Start driver on port 50050
python -m sila2.driver.thermoscientific.teleshake1536 --port 50050
```

### Connect to the SiLA server

Run the Universal SiLA Client. You can run the SiLA client following the instructions here 
Open your browser and connect to `localhost/8080`, you should see the following screen:
Press add server.
You should see the server added in the bottom of the screen. Select it and then click the play button on the left side of the screen.
Now you should be able to run the driver commands.

### Contributing

We are always looking to contribution for new drivers, we want to expand this library as much as possible to make automation easy, standardized and available to anyone. All new driver should follow the folder structure presented above. All drivers should follow our naming convention as well as the data format for output. If you are in doubt, please contribute with new drivers and we will help and make them compliant with our standards.
Authors and acknowledgment
Show your appreciation to those who have contributed to the project.

### Project status
All the drivers here are functional, however they are still under development to comply with data models and standards.

