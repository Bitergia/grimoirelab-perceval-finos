# perceval-finos [![Build Status](https://travis-ci.org/Bitergia/grimoirelab-perceval-finos.svg?branch=master)](https://travis-ci.org/Bitergia/grimoirelab-perceval-finos) [![Coverage Status](https://img.shields.io/coveralls/Bitergia/grimoirelab-perceval-finos.svg)](https://coveralls.io/r/Bitergia/grimoirelab-perceval-finos?branch=master)

Bundle of Perceval backends for FINOS ecosystem.

## Backends

The backends currently managed by this package support the next repositories:

* FINOS meetings attendance

## Requirements

* Python >= 3.4
* python3-requests >= 2.7
* grimoirelab-toolkit >= 0.1.9
* perceval >= 0.12

## Installation

To install this package you will need to clone the repository first:

```
$ git clone https://github.com/Bitergia/grimoirelab-perceval-finos.git
```

Then you can execute the following commands:
```
$ pip3 install -r requirements.txt
$ pip3 install -e .
```

In case you are a developer, you should execute the following commands to install Perceval in your working directory (option `-e`) and the packages of requirements_tests.txt.
```
$ pip3 install -r requirements.txt
$ pip3 install -r requirements_tests.txt
$ pip3 install -e .
```

## Examples

### FINOS meetings

#### Locating via URL

```
$ perceval finosmeetings https://gist.githubusercontent.com/maoo/27db80e0dba349caf95cd3f2af909fe8/raw/d8bdc91ed1ac2c0e5b8e0dc95d5248527c88260d/finos-meetings.csv
```

#### Locating via file path

```
$ perceval finosmeetings file:///Users/m/w/projects/metadata-tool/roster-data.csv
```

## License

Licensed under GNU General Public License (GPL), version 3 or later.
