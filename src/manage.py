# -*- coding: utf-8 -*-
from time import sleep
import logging
import subprocess
from src.env import init_env
from src.detector import Detector
from src.downloader import Downloader


class Manager(object):
    def __init__(self):
        init_env()
        self._dt = Detector()
        self._dl = Downloader()

    def execute(self):
        while matchInfo := self._dt.get_one_match():
            # download demo
            self._dl.set_matchInfo(matchInfo)
            self._dl.start_download()
            demopaths = self._dl.export_demos()
            for demopath in demopaths:
                if subprocess.run(['sh', 'scripts/parse_demo.sh', demopath]).returncode != 0:
                    logging.error(f'parse_demo.sh failed: {demopath}')
                else:
                    logging.info('parse_demo.sh success')
            sleep(1.0)


manager = Manager()
