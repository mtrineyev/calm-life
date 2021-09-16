"""
Stop the process of hanging scraping jobs

For detailed setup, deployment and run instructions see readme.md file

© 2021 MediaMonitoringBot, written by Maksym Trineyev
"""

import logging
from os import system
import requests
import yaml

try:
    with open('config.yaml', 'r') as f_cfg:
        cfg = yaml.safe_load(f_cfg)
except FileNotFoundError:
    logging.critical('config.yaml not found')
    exit(1)

logging.basicConfig(
    filename=cfg['logging']['file'],
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=int(cfg['logging']['level']))


class ActiveProcesses:
    """
    Get list of the currently running scrapy jobs (aka 'processes')
    and terminate old hanging ones
    """
    proc_file = cfg['main']['cur_proc_file']
    seen_proc_file = cfg['main']['seen_proc_file']
    processes_list = f"{cfg['main']['processes_list_command']} > {proc_file}"
    kill_command = cfg['main']['kill_command']
    process_name_column_number = cfg['main']['process_name_column_number']
    process_name = cfg['main']['process_name'].lower()
    pid_column_number = cfg['main']['pid_column_number']
    bucket_column_number = cfg['main']['bucket_column_number']
    seen_times = cfg['main']['seen_times']
    server_name = cfg['main']['server_name']
    heath_check_url = cfg['healthcheck']['check_url']
    slack_webhook = cfg['healthcheck']['slack_webhook']

    def __init__(self) -> None:
        if not all((
            self.process_name_column_number > 0,
            self.pid_column_number > 0,
            self.bucket_column_number > 0,
        )):
            logging.critical('All column number parameters must be positive. Terminated')
            exit(2)
        if self.heath_check_url:
            requests.get(f'{self.heath_check_url}/start', timeout=5)
        try:
            with open(self.seen_proc_file, 'r') as f:
                self.seen_processes = yaml.safe_load(f)
            logging.info(f'Read {len(self.seen_processes)} seen processes.')
        except (FileNotFoundError, TypeError):
            logging.warning(f'File "{self.seen_proc_file}" not found. Used empty one.')
            self.seen_processes = dict()
        if self.get_current_processes():
            self.terminate_hang_processes()
            self.save_seen_processes()

    def get_current_processes(self) -> int:
        """
        Call OS command of list processes, parse python processes and count process seen times
        """
        current_processes = dict()
        returned_value = system(self.processes_list)
        if returned_value and returned_value != 256:
            # code 256 means there are no active processes for the user
            logging.warning(f'Processes list terminated with error {returned_value}.')
            return False
        with open(self.proc_file, 'r') as f:
            processes = f.readlines()
        max_column_number = max((self.process_name_column_number, self.pid_column_number, self.bucket_column_number))
        for process in processes:
            parsed = process.lower().split()
            if (
                max_column_number <= len(parsed) and
                parsed[self.process_name_column_number - 1] == self.process_name
            ):
                process_number = parsed[self.pid_column_number - 1]
                current_processes[process_number] = dict(
                    seen=0,
                    bucket=parsed[self.bucket_column_number - 1]
                )
                current_processes[process_number]['seen'] = \
                    self.seen_processes.get(process_number, dict(seen=0))['seen'] + 1
        self.seen_processes = current_processes
        return True

    def terminate_hang_processes(self) -> None:
        """
        Find processes seen more then self.seen_times and kill them
        """
        for key, value in self.seen_processes.items():
            if value['seen'] >= self.seen_times:
                returned_value = system(f'{self.kill_command} {key}')
                if returned_value:
                    logging.error(f'Can\'t kill process {key}.')
                else:
                    msg = f'Killed process {key} for bucket {value["bucket"]} at {self.server_name}.'
                    logging.warning(msg)
                    if self.slack_webhook:
                        try:
                            requests.post(self.slack_webhook, json={
                                'username': 'Frozen buckets auto-killer',
                                'icon_emoji': ':skull:',
                                'text': msg
                            })
                        except requests.exceptions.ConnectionError:
                            logging.warning('Connection to Slack error, alarm did not send.')
                    self.seen_processes[key]['seen'] = 0
        self.seen_processes = {k: v for k, v in self.seen_processes.items() if v['seen']}

    def save_seen_processes(self) -> None:
        """
        Save information about the seen processes
        """
        logging.info(f'Saving {len(self.seen_processes)} current processes.')
        with open(self.seen_proc_file, 'w') as f:
            yaml.dump(self.seen_processes, f)
        if self.heath_check_url:
            requests.get(self.heath_check_url)


if __name__ == '__main__':
    p = ActiveProcesses()

