import argparse
import signal
import sys

from loguru import logger

from .configure import write_configuration
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
    parser.add_argument('--show-config',
                        action='store_true',
                        help='Show the current configuration and exit')
    parser.add_argument('--configure',
                        action='store_true',
                        help='Configure pyup')
    parser.add_argument('--save-logs',
                        help='Save logs to a file',
                        action='store_true')
    parser.add_argument('files', nargs='*', help='Path of files to upload')
    return parser.parse_args()


def main():
    args = opts()

    if args.configure:
        write_configuration()

    pyup = PyUp(args.files,
                domain_name=args.domain_name,
                keep_name=args.keep_name,
                overwrite=args.overwrite,
                local_only=args.local_only,
                no_notifications=args.no_notifications,
                verbosity_level=args.verbosity_level,
                parallel=args.parallel,
                show_config=args.show_config,
                save_logs=args.save_logs)
    pyup.main()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, keyboard_interrupt_handler)
    main()
