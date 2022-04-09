# -*- coding: utf-8 -*-
'''
check if the environment is compatible with the program.
'''

import platform
import subprocess
import socket
import os
import logging
from sys import version_info as vinfo


def __is_net_ok(host: str) -> bool:
    '''    
    return if network is fine when connect host
    '''
    soc = socket.socket()
    soc.settimeout(1)
    try:
        soc.connect((host, 80))
        return True
    except:
        return False


def __env_check():
    '''
    raise an exception if the environment is not compatible.
    '''
    if not (vinfo.major == 3 and vinfo.minor >= 8):
        raise Exception('Python 3.8 or later is required.')
    if (_os := platform.system()) != 'Linux':
        raise Exception(f'OS Linux is required. Current system is {_os}.')
    if subprocess.run(['sh', 'scripts/check_dependencies.sh']).returncode != 0:
        raise Exception('Dependencies are not installed.')
    if not __is_net_ok('hltv.org'):
        raise Exception('Network is not available.')
    if not os.path.exists('config.toml'):
        raise Exception('config.toml is not found.')
    if not os.path.exists('minidemo-encoder'):
        raise Exception('minidemo-encoder is not found.')


def init_env():
    __env_check()
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(asctime)s:%(message)s',
        datefmt='%Y-%d-%m %H:%M:%S'
    )
