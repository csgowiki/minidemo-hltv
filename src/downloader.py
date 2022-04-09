# -*- coding: utf-8 -*-

import os
import logging
import shutil
import requests
import subprocess
from tqdm import tqdm

from src.model import MatchInfo


class Downloader(object):
    def __init__(self):
        self._headers = {
            'User-Agent': (
                'Mozilla/5.0 '
                '(iPhone; CPU iPhone OS 13_2_3 like Mac OS X) '
                'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                'Version/13.0.3 Mobile/15E148 Safari/604.1'
            ),
            'Referer': 'https://hltv.org'
        }
        self._dl_dir = 'download_temp'
        self._matchInfo = None
        self._rar_path = None

    def set_matchInfo(self, matchInfo: MatchInfo):
        self._matchInfo = matchInfo

    def start_download(self) -> bool:
        if not self._matchInfo or len(self._matchInfo.demoLink) == 0:
            return False

        if os.path.exists(self._dl_dir):
            shutil.rmtree(self._dl_dir)
        os.mkdir(self._dl_dir)

        _dl_filename = f'{self._matchInfo.demoLink.split("/")[-1]}.rar'
        _url = f"https://hltv.org{self._matchInfo.demoLink}"
        resp = requests.get(_url, headers=self._headers, stream=True)
        if resp.status_code != requests.codes.ok:
            return False

        file_size_bytes = float(resp.headers['Content-Length'])
        self._rar_path = os.path.join(self._dl_dir, _dl_filename)
        logging.info(f"<{self._rar_path}> {file_size_bytes}bytes")
        _cksize = 1024
        try:
            with open(self._rar_path, 'ab') as demoFile:
                for chunk in tqdm(
                    resp.iter_content(chunk_size=_cksize),
                    desc="downloading",
                    total=file_size_bytes/_cksize,
                    unit='B',
                    unit_scale=True,
                    mininterval=10.0
                ):
                    if not chunk:
                        continue
                    demoFile.write(chunk)
                    demoFile.flush()
        except Exception as ept:
            logging.error(f"<{self._rar_path}> {ept}")
            return False
        return True

    def export_demos(self) -> list:
        if subprocess.run(['unrar', 'x', self._rar_path, self._dl_dir]).returncode != 0:
            logging.error(f"<{self._rar_path}> unrar failed")
        os.remove(self._rar_path)
        return list(map(
            lambda x: os.path.join(self._dl_dir, x),
            os.listdir(self._dl_dir)
        ))