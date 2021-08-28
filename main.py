"""
Stop the process of hanging scraping jobs

For detailed setup, deployment and run instructions see readme.md file

© 2021 MediaMonitoringBot, written by Maksym Trineiev
"""

from configparser import ConfigParser
import logging
from os import system
import pickle
import requests

config = ConfigParser()
config.read('config.ini')
logging.basicConfig(
    filename=config['Logging']['FILE_NAME'],
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=int(config['Logging']['LEVEL']))


class ActiveProcesses:
    """
    Get list of the currently running scrapy jobs (aka 'processes')
    and terminate old hanging ones
    """
    proc_file = config['Main']['PROC_FILE']
    pickle_file = config['Main']['PICKLE_FILE']
    processes_list = f"{config['Main']['PROCESSES_LIST']} > {proc_file}"
    kill_command = config['Main']['KILL_COMMAND']
    process_name = config['Main']['PROCESS_NAME'].lower()
    seen_times = config['Main'].getint('SEEN_TIMES')
    heath_check_url = config['Misc']['HEALTH_CHECK_URL']
    slack_webhook = config['Misc']['SLACK_MEDIAMONITORINGBOT_WEBHOOK']

    def __init__(self) -> None:
        if self.heath_check_url:
            requests.get(f'{self.heath_check_url}/start', timeout=5)
        try:
            with open(self.pickle_file, 'rb') as f:
                self.seen_processes = pickle.load(f)
            logging.info(f'Read {len(self.seen_processes)} seen processes.')
        except FileNotFoundError:
            logging.warning(f'File "{self.pickle_file}" not found. Used empty one.')
            self.seen_processes = dict()
        return

    def get_current_processes(self) -> int:
        """
        Call OS command of list processes, parse python processes
        and count process seen times
        """
        current_processes = dict()
        returned_value = system(self.processes_list)
        if returned_value and returned_value != 256:
            # code 256 means there are no active processes for the user
            logging.warning(f'Processes list terminated with error {returned_value}.')
            return returned_value
        with open(self.proc_file, 'r') as f:
            processes = f.readlines()
        for process in processes:
            parsed = process.strip().lower().split(' ')
            if parsed[-1] == self.process_name:
                process_number = parsed[0]
                current_processes[process_number] = self.seen_processes.get(process_number, 0) + 1
        self.seen_processes = current_processes
        return 0

    def terminate_hang_processes(self) -> None:
        """
        Find processes seen more then self.seen_times
        and kill them
        """
        for key, value in self.seen_processes.items():
            if value >= self.seen_times:
                returned_value = system(f'{self.kill_command} {key}')
                if returned_value:
                    logging.error(f'Can\'t kill PID {key}.')
                else:
                    logging.warning(f'Killed process with PID {key}.')
                    self.seen_processes[key] = 0
        self.seen_processes = {k: v for k, v in self.seen_processes.items() if v}
        return

    def save_seen_processes(self) -> None:
        """
        Save count of seen processes
        @return: None
        """
        logging.info(f'Saving {len(self.seen_processes)} current processes.')
        with open(self.pickle_file, 'wb') as f:
            pickle.dump(self.seen_processes, f)
        if self.heath_check_url:
            requests.get(self.heath_check_url)
        return


if __name__ == '__main__':
    p = ActiveProcesses()
    p.get_current_processes()
    p.terminate_hang_processes()
    p.save_seen_processes()
