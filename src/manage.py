# -*- coding: utf-8 -*-
from src.env import init_env
from src.detector import Detector

class Manager(object):
    def __init__(self):
        init_env()
        self.detector = Detector()
        pass

    def execute(self):
        __continue = True
        while __continue:
            __continue, matchInfo = self.detector.get_one_match()
            # TODO: download demo

            # TODO: parse demo

            # TODO: upload record file to server

manager = Manager()
