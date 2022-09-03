# pyup

# Getting Started

- On the server host machine:

1. Clone the repo:

```shell
git clone https://github.com/Alyetama/pyup.git
```

2. Rename and update `.env`:

```shell
mv .env.example .env
nano .env  # or any other text editor
docker-compose up -d
```

- Copy the `.env` file from the server host to the client machine (where you will upload from), then, run:

```shell
mv .env ~/.pyup
```

## Install

```shell
pip install pyup
```

## Basic Usage

```
usage: pyup [-h] [-d DOMAIN_NAME] [-k] [--overwrite] [-l] [--no-notifications] [-v {0,1,2,3,4,5}] [-p]
            [--save-logs]
            [files ...]

positional arguments:
  files                 Files to upload

options:
  -h, --help            show this help message and exit
  -d DOMAIN_NAME, --domain-name DOMAIN_NAME
                        The domain name to use for the URL
  -k, --keep-name       Keep the original file name
  --overwrite           Overwrite if name is kept and the file name already exists on the server
  -l, --local-only      Allow uploads from local IP addresses only
  --no-notifications    Suppress notifications (notifications are supported on macOS only)
  -v {0,1,2,3,4,5}, --verbosity-level {0,1,2,3,4,5}
                        Set the logging verbosity level
  -p, --parallel        Upload files in parallel
  --save-logs           Save logs to a file
```
