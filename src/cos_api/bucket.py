# -*- coding=utf-8 -*-
import os
import logging
import json
import time
import requests
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tqdm import tqdm
from ..model import MatchInfo

class BucketAPI(object):
    def __init__(self):
        _secret_id = os.getenv('COS_SECRETID')
        _secret_key = os.getenv('COS_SECRETKEY')
        self.bucket_name = os.getenv('COS_BUCKETNAME')
        self.region = os.getenv('COS_REGION')
        _region = 'ap-chengdu'
        _config = CosConfig(Region=_region, SecretId=_secret_id, SecretKey=_secret_key)
        self.cos_client = CosS3Client(_config)

    def list_matches(self, mapname: str) -> list: # ['de_inferno/123123/']
        contents = []
        while True:
            response = self.cos_client.list_objects(
                Bucket=self.bucket_name,
                Prefix=mapname + '/',
                Delimiter='/'
            )
            if 'CommonPrefixes' in response:
                contents.extend(map(lambda x: x['Prefix'],
                    filter(lambda x: 'Prefix' in x, response['CommonPrefixes'])))
            if response['IsTruncated'] == 'false':
                break
        return contents

    def __upload_file(self, key: str, path: str):
        self.cos_client.upload_file(
            Bucket=self.bucket_name,
            Key=key,
            LocalFilePath=path,
        )
        time.sleep(0.1)

    def __delete_prefix(self, prefix: str):
        logging.warning('deleting %s', prefix)
        is_over = False
        marker = ''
        while not is_over:
            response = self.cos_client.list_objects(Bucket=self.bucket_name, Prefix=prefix, Marker=marker)
            if response['Contents']:
                for content in response['Contents']:
                    self.cos_client.delete_object(Bucket=self.bucket_name, Key=content['Key'])
                if response['IsTruncated'] == 'false':
                    is_over = True
                    marker = response['Marker']

    def upload_match(self, matchId: int, mapname: str, maxreserve: int = 5):
        areadyList = self.list_matches(mapname)
        if f'{mapname}/{matchId}/' in areadyList:
            logging.warning(f'{mapname}/{matchId}/ already uploaded')
            return
        if len(areadyList) >= maxreserve:
            logging.warning(f'{mapname}/{matchId}/ already full, start to delete')
            logging.warning('LIST:', areadyList)
            self.__delete_prefix(areadyList[-1])
            return

        base_dir = 'minidemo-encoder/output'
        logging.info('uploading match %s', matchId)
        for round_key in tqdm(os.listdir(base_dir), desc='uploading', mininterval=1.0):
            _dir = os.path.join(base_dir, round_key)
            for torct in os.listdir(_dir):
                _subdir = os.path.join(_dir, torct)
                for player_key in os.listdir(_subdir):
                    _finalpath = os.path.join(_subdir, player_key)
                    _key = '/'.join([mapname, str(matchId), round_key, torct, player_key])
                    self.__upload_file(_key, _finalpath)
        logging.info('uploading match %s done', matchId)

    def update_index(self, mapname: str, match_info: MatchInfo):
        # call after upload_match
        flist = []

        basedir = 'minidemo-encoder/output'

        for path, _, file_list in os.walk(basedir):
            for file_name in file_list:
                flist.append(os.path.join(path, file_name))

        roundlist = list(set(map(lambda x: int(x.split('/')[2].replace('round', '')), flist)))
        roundlist.sort()
        match_info.maxround = roundlist[-1] + 1

        for rd in range(match_info.maxround):
            if os.path.exists(f'{basedir}/round{rd}/ct/{match_info.team1.players[0]}.rec'):
                match_info.team1.ctRounds.append(rd)
            if os.path.exists(f'{basedir}/round{rd}/ct/{match_info.team2.players[0]}.rec'):
                match_info.team2.ctRounds.append(rd)
        match_dict = match_info.dict()

        logging.warning(f'update index: {match_dict}')

        # fetch index
        index_dict = {}
        response = self.cos_client.object_exists(
            Bucket=self.bucket_name,
            Key=f'{mapname}/index.json'
        )
        if response:
            index_dict = requests.get(f'https://{self.bucket_name}.cos.{self.region}.myqcloud.com/{mapname}/index.json').json()
        index_dict[str(match_info.matchId)] = match_dict

        with open(f'{basedir}/index.json', 'w') as f:
            json.dump(index_dict, f)

        self.__upload_file(f'{mapname}/index.json', f'{basedir}/index.json')
