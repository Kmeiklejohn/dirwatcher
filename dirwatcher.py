#! /usr/bin/env/python3
"""
Dir watcher this will contain a long running program
"""

__author__ = "Kmeiklejohn"

import argparse
import signal
import logging
import time
import os
import datetime
import glob
import sys

exit_flag = False

logger = logging.getLogger(__name__)


def create_parser():
    """ Creates arguments that will take in a intervals, file ext,
        The path to watch, and a magic string
    """
    parser = argparse.ArgumentParser(
        description="Picking dirwatcher attr")
    parser.add_argument(
        '-i',
        '--interval',
        type=float,
        nargs='?',
        default=1.0,
        help='polling intervals for dirwatcher')
    parser.add_argument(
        '-e',
        '--ext',
        type=str,
        nargs='?',
        default='.txt',
        help='enter a file extention'
    )
    parser.add_argument(
        '-p',
        '--path',
        type=str,
        nargs='?',
        help='enter a file path'
    )
    parser.add_argument(
        '-m',
        '--magic',
        nargs='?',
        default=None,
        help="a string to watch"
    )

    return parser


def raise_exit_flag():
    """Sets the exit flag"""
    global exit_flag
    exit_flag = True

def reading_files(args):
    """This reads in a file and stores in a string"""
    list_text = []
    path = glob.glob(f'{args.path}/*')
    for filename in path:        
        with open(filename, 'r') as file:
            lines = file.readlines()
            list_text.append(lines)
            
    return list_text, filename
       
    

def magic_text(args):
    """This function searches a file for a magic string"""
    files, filename = reading_files(args)
    magic_dict = {}
    for file in files:
        for counter, line in enumerate(file, start=1):
            if args.magic in line:
                magic_dict.update({counter: line})
                logger.info(f'File: {filename}, Found: {args.magic} on line {counter}')
                time.sleep(args.interval)
    return magic_dict


def dir_watcher(args):
    """Finds a directory to watch and logs info, errors and warnings"""
    logger.info(f'Watching directory: {args.path}, File Ext: {args.ext}, Polling Interval: {args.interval}, Magic Text: {args.magic}')

    while not exit_flag:
        try:
            magic_text(args)
            time.sleep(args.interval)
        except Exception as e:
            logger.error('\n------------------\n'
                         f'Error\n{e}'
                         '\n------------------\n')
            time.sleep(3)


def signal_handler(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    # log the associated signal name (the python3 way)
    # log the signal name (the python2 way)
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
                    if v.startswith('SIG') and not v.startswith('SIG_'))
    raise_exit_flag()
    logger.warning(f'\n Received {signames[sig_num]}')


def main(args):
    """This is the main function that sels signals and logging info"""
    polling = float(args.interval)
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    # Now my signal_handler will get called if OS sends either of these to my
    # process.
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler(f"{args.path}.log"),
            logging.StreamHandler()
        ])
    logger.info('\n----------------------------\n'
                'Starting Dirwatcher\n'
                '----------------------------\n')
    first_time = datetime.datetime.now()
    while not exit_flag:

        time.sleep(polling)

        try:
            logger.info(f'Monitoring {args.path}')
            dir_watcher(args)
        except Exception as e:
            logger.error('\n------------------\n'
                         f'Error{e}\n'
                         '------------------\n')
    logger.warning('\n----------------------------\n'
                   'Shutting Down.....\n'
                   '----------------------------')
    # final exit point happens here
    # Log a message that we are shutting down
    # Include the overall uptime since program start.
    last_time = datetime.datetime.now()
    uptime = last_time - first_time
    print("Uptime was", uptime)
    logging.shutdown()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = create_parser()
    args = parser.parse_args()
    main(args)
