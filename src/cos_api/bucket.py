# -*- coding=utf-8 -*-
import os
import logging
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tqdm import tqdm

class BucketAPI(object):
    def __init__(self):
        _secret_id = os.getenv('env.TENCENTCLOUDSECRETID')
        _secret_key = os.getenv('env.TENCENTCLOUDSECRETKEY')
        _region = 'ap-chengdu'
        _config = CosConfig(Region=_region, SecretId=_secret_id, SecretKey=_secret_key)
        self.cos_client = CosS3Client(_config)
        self.bucket_name = os.getenv('env.TENCENTCOUDBUCKETNAME')

    def list_matches(self, mapname: str) -> list: # 'de_inferno/123123/'
        response = self.cos_client.list_objects(
            Bucket=self.bucket_name,
            Prefix=mapname + '/',
            Delimiter='/'
        )
        return list(map(lambda x: x['Prefix'], response['CommonPrefixes']))
    
    def __upload_file(self, key: str, path: str):
        self.cos_client.upload_file(
            Bucket=self.bucket_name,
            Key=key,
            LocalFilePath=path,
        )

    def upload_match(self, matchId: int, mapname: str):
        areadyList = self.list_matches(mapname)
        if f'{mapname}/{matchId}/' in areadyList:
            logging.warning(f'{mapname}/{matchId}/ already uploaded')
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