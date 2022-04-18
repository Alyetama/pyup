# Caddy Fileserver

## Install

```shell
pip install pyup
```

## Getting started

```shell
mv .env.example .env
nano .env  # or any other text editor
docker-compose up -d
```

- Configure `pyup`:

```shell
pyup --configure
```

## Basic Usage

```
usage: pyup [-h] [-d DOMAIN_NAME] [-k] [--overwrite] [-l] [--no-notifications]
            [-v {0,1,2,3,4,5}] [-p] [--show-config] [--configure]
            [--save-logs]
            [files ...]

positional arguments:
  files                 Path of files to upload

optional arguments:
  -h, --help            show this help message and exit
  -d DOMAIN_NAME, --domain-name DOMAIN_NAME
                        The domain name to use for the URL
  -k, --keep-name       Keep the original file name
  --overwrite           Overwrite if name is kept and the file name already
                        exists on the server
  -l, --local-only      Allow uploads from local IP addresses only
  --no-notifications    Suppress notifications (notifications are supported on
                        macOS only)
  -v {0,1,2,3,4,5}, --verbosity-level {0,1,2,3,4,5}
                        Set the logging verbosity level
  -p, --parallel        Upload files in parallel
  --show-config         Show the current configuration and exit
  --configure           Configure pyup
  --save-logs           Save logs to a file
```
