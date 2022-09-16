#!/usr/bin/env python
# coding: utf-8

import argparse
import signal
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from .pyup import PyUp


def keyboard_interrupt_handler(sig, _):
    logger.warning(f'KeyboardInterrupt (ID: {sig}) has been caught...')
    logger.warning('Terminating the session gracefully...')
    sys.exit(1)


def opts():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d',
                        '--domain-name',
                        default=None,
                        help='The domain name to use for the URL',
                        type=str)
    parser.add_argument('-k',
                        '--keep-name',
                        action='store_true',
                        help='Keep the original file name')
    parser.add_argument('--overwrite',
                        action='store_true',
                        help='Overwrite if name is kept and the file name ' \
                        'already exists on the server')
    parser.add_argument('-l',
                        '--local-only',
                        action='store_true',
                        help='Allow uploads from local IP addresses only')
    parser.add_argument('--no-notifications',
                        action='store_true',
                        help='Suppress notifications (notifications are ' \
                        'supported on macOS only)')
    parser.add_argument('-v',
                        '--verbosity-level',
                        choices=range(6),
                        default=0,
                        help='Set the logging verbosity level',
                        type=int)
    parser.add_argument('-p',
                        '--parallel',
                        action='store_true',
                        help='Upload files in parallel')
    parser.add_argument('--save-logs',
                        help='Save logs to a file',
                        action='store_true')
    parser.add_argument('files', nargs='*', help='Files to upload')
    return parser.parse_args()


def main():
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    env_file = Path.home() / '.pyup'
    if not env_file.exists():
        logger.error(f'Could not find the configuration file: `{env_file}`!')
        sys.exit(1)
    load_dotenv(env_file)

    args = opts()

    pyup = PyUp(args.files,
                domain_name=args.domain_name,
                keep_name=args.keep_name,
                overwrite=args.overwrite,
                local_only=args.local_only,
                no_notifications=args.no_notifications,
                verbosity_level=args.verbosity_level,
                parallel=args.parallel,
                save_logs=args.save_logs)
    pyup.run()


if __name__ == '__main__':
    main()
