#!/usr/bin/env python
# coding: utf-8

import concurrent.futures
import datetime
import hashlib
import ipaddress
import mimetypes
import os
import platform
import shlex
import shutil
import socket
import subprocess
import sys
import time
import uuid
from pathlib import Path

import paramiko
import pymongo
import pyperclip
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table


class PyUp:

    def __init__(self,
                 files,
                 domain_name=None,
                 keep_name=False,
                 overwrite=False,
                 local_only=False,
                 no_notifications=False,
                 verbosity_level=0,
                 parallel=False,
                 show_config=False,
                 save_logs=False):
        self.files = files
        self.domain_name = domain_name
        self.keep_name = keep_name
        self.overwrite = overwrite
        self.local_only = local_only
        self.no_notifications = no_notifications
        self.verbosity_level = verbosity_level
        self.parallel = parallel
        self.show_config = show_config
        self.save_logs = save_logs

    @staticmethod
    def is_remote():
        if os.getenv('FILSERVER_HOST') and os.getenv('FILSERVER_USERNAME'):
            return True

    def get_logger(self):
        if self.verbosity_level == 0:
            level = 5
        else:
            level = self.verbosity_level * 10
        logger.remove()
        logger.add(
            sys.stderr,
            format='{level.icon} <fg #3bd6c6>{time:HH:mm:ss}</fg #3bd6c6> | '
            '<level>{level: <8}</level> | '
            '<fg #f1fa8c>ln:{line: <4}</fg #f1fa8c> - <lvl>{message}</lvl>',
            level=level)
        logger.level('WARNING', color='<yellow><bold>', icon='🚧')
        logger.level('INFO', color='<bold>', icon='🚀')
        if self.save_logs:
            logger.add('pyup.log', level=level)
        return logger

    @staticmethod
    def notification(title, subtitle=None, message=None):
        notifier_bin = shutil.which('terminal-notifier')
        if notifier_bin:
            subprocess.run(
                shlex.split(
                    f'{notifier_bin} -title \"{title}\" '
                    f'-subtitle \"{subtitle}\" -message \"{message}\"'))

    def check_host(self):
        if not os.getenv('FILSERVER_HOST'):
            return
        exit_code = os.system(f'ping -c 1 -W 1 {os.environ["FILSERVER_HOST"]} '
                              '> /dev/null 2>&1')
        if exit_code != 0:
            self.notification('Host server is down!')
            logger.error('Server is down!')
            sys.exit(1)

        host = socket.gethostname()
        local_ip = ipaddress.ip_address(socket.gethostbyname(host))
        logger.debug(f'📥 Received a request from `{host}`')
        subnet = ipaddress.ip_network(f'{local_ip}/255.255.255.0',
                                      strict=False)
        if self.local_only and local_ip not in subnet:
            raise ConnectionRefusedError
        return

    @staticmethod
    def create_server_client():
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(os.environ['FILSERVER_HOST'],
                       username=os.environ['FILSERVER_USERNAME'],
                       key_filename=os.getenv('SSH_PRIVATE_KEY_PATH'))
        return client

    @staticmethod
    def create_mongodb_client():
        username = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        host = os.getenv('MONGODB_HOST')
        port = os.getenv('MONGODB_PORT')
        if all(x for x in [username, password, host, port]):
            mongodb_con_str = f'mongodb://{username}:{password}@{host}:{port}'
            client = pymongo.MongoClient(mongodb_con_str,
                                         serverSelectionTimeoutMS=2000)
        else:
            logger.warning('No database configured...')
            return
        return client.fileserver_db

    def mongodb_insert(self, db, file_data):
        try:
            return db.files.insert_one(file_data)
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.error('MongoDB timed out!')
        except pymongo.errors.OperationFailure:
            logger.error('Failed to inset the record due to an authentication '
                         'error! Check your MongoDB username/password!')
        except Exception as e:
            logger.exception(e)

    def upload(self, file, db, server_client):
        start = time.time()
        id_ = str(uuid.uuid4()).split('-')[0]

        if self.keep_name:
            existing_names = db.files.find().distinct('original_file_name')
            if Path(file).name in existing_names and not self.overwrite:
                raise FileExistsError(
                    '\033[31mA URL with the same file name '
                    'already exists! If you want to overwrite, '
                    'pass `--overwrite`.\033[49m')
            out_filename = Path(file).name.replace(' ', '_')
        else:
            out_filename = f'{id_}{Path(file).suffix}'

        logger.debug(f'📤 Uploading "{file}" with id "{id_}" ...')
        file_dest = str(
            Path(f'{os.environ["FILESERVER_DATA_PATH"]}/{out_filename}').
            absolute())
        if self.is_remote():
            sftp = server_client.open_sftp()
            sftp.put(file, file_dest)
        else:
            shutil.copy(file, file_dest)

        fs_host = os.getenv('FILESERVER_PORT')
        fs_port = os.getenv('FILESERVER_PORT')

        if self.domain_name:
            url = f'https://{self.domain_name}/{out_filename}'
        elif os.getenv('DEFAULT_DOMAIN_NAME'):
            url = f'https://{os.environ["DEFAULT_DOMAIN_NAME"]}/{out_filename}'
        elif fs_host:
            url = f'http://{fs_host}:{fs_port}/{out_filename}'
        else:
            url = f'http://127.0.0.1:{fs_port}/{out_filename}'
        logger.debug(f'✅ File was uploaded successfully!')
        logger.info(f'"{file}" -> 🚀 \033[32m{url}\033[39m')

        file_data = {
            '_id': id_,
            'md5_checksum': hashlib.md5(Path(file).read_bytes()).hexdigest(),
            'created_at': time.ctime(Path(file).stat().st_ctime),
            'original_file_name': Path(file).name,
            'url_file_name': Path(out_filename).name,
            'url': url,
            'size_bytes': Path(file).stat().st_size,
            'mimetype': mimetypes.guess_type(file)[0],
            'processing_time':
            str(datetime.timedelta(seconds=time.time() - start))
        }

        if not self.parallel:
            try:
                pyperclip.copy(file_data['url'])
            except pyperclip.PyperclipException as e:
                logger.trace(e)

        if 'macOS' in platform.platform():
            try:
                self.notification('Upload complete!',
                                  f'Took {round(time.time() - start, 2)}s',
                                  file_data['url'])
            except FileNotFoundError:
                logger.warning('Install terminal-notifier for notifications! '
                               '(optional)\n$ brew install terminal-notifier')
            except subprocess.CalledProcessError as e:
                logger.trace(
                    'on macOS, and `terminal-notifier` is installed, '
                    f'but failed to send notification! Received error: {e}')

        self.mongodb_insert(db, file_data)
        logger.debug('🍃 Inserted the file into the database successfully!')

        if self.is_remote():
            sftp.close()
        return file, file_data['url']

    def run(self):
        load_dotenv(Path.home() / '.pyup')
        console = Console()
        logger = self.get_logger()

        start = time.time()
        self.check_host()

        db = self.create_mongodb_client()
        if self.is_remote():
            server_client = self.create_server_client()
        else:
            server_client = None

        if isinstance(self.files, str):
            self.files = [self.files]

        if self.parallel:
            with concurrent.futures.ThreadPoolExecutor() as executor:

                futures = [
                    executor.submit(self.upload, file, db, server_client)
                    for file in self.files
                ]

                results = []
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

        else:
            results = []
            for file in self.files:
                results.append(self.upload(file, db, server_client))

        if self.is_remote():
            server_client.close()
        logger.debug(f'⏲️  Took {round(time.time() - start, 2)}s')

        table = Table(show_header=True,
                      header_style="bold #50fa7b",
                      show_lines=True)
        table.add_column('File', style='#f1fa8c', justify='left')
        table.add_column('URL', style='#8be9fd')
        for result in results:
            table.add_row(*result)
        console.print(table)

        return results
