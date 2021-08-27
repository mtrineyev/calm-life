"""
Show list of the saved seen scrapy processes with its count

© 2021 MediaMonitoringBot, written by Maksym Trineiev
"""

from configparser import ConfigParser
import pickle

config = ConfigParser()
config.read('config.ini')


if __name__ == '__main__':
    pickle_file = config['Main']['PICKLE_FILE']
    try:
        with open(pickle_file, 'rb') as f:
            seen_processes = pickle.load(f)
        print('Seen processes with its count:', seen_processes)
    except FileNotFoundError:
        print(f'File "{pickle_file}" not found.')
