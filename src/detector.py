# -*- coding: utf-8 -*-
from typing import Tuple
import time
import datetime
import toml
import requests
from src.model import MatchInfo


class Detector(object):
    '''
    request https://hltv.org and parse infomation    
    '''

    def __init__(self):
        self.config = toml.load('config.toml')
        self.matches = []
        self.__request_today_matches()
        self.ptr = 0  # the index of current match

    def __match_filter(self, match: dict) -> bool:
        return (
            match['stars'] >= self.config['subscription']['stars_min'] and
            (match['date'] / 1000 - time.time()) / 3600 <= 24 * 10
        )

    def __contact_api(self, api: str) -> str:
        return f"{self.config['hltv-api']['endpoint']}{self.config['hltv-api'][api]}"

    def __request_today_matches(self):
        _now = datetime.datetime.now()
        todayStr = _now.strftime('%Y-%m-%d')
        yesterdayStr = (_now - datetime.timedelta(days=10)).strftime('%Y-%m-%d')
        _url = f"{self.__contact_api('results')}?startDate={yesterdayStr}&endDate={todayStr}"
        self.matches = list(
            filter(self.__match_filter, requests.get(_url).json()))

    def get_one_match(self) -> MatchInfo:
        '''
        return matchInfo if there is a match
        return None if there is no match
        '''
        if self.ptr >= len(self.matches):
            return None

        _url = f"{self.__contact_api('match')}?id={self.matches[self.ptr]['id']}"
        resp = requests.get(_url).json()

        demoLink = ''
        # assume idx 0 is demolink
        if len(resp['demos']) > 0 and resp['demos'][0]['name'] == 'GOTV Demo':
            demoLink = resp['demos'][0]['link']
        
        matchInfo = MatchInfo(**{
            'matchId': resp['id'],
            'demoLink': demoLink,
            'timestamp': self.matches[self.ptr]['date'],
            'date': time.strftime('%Y-%m-%d', time.localtime(self.matches[self.ptr]['date'] / 1000)),
            'eventName': resp['event']['name'],
            'mformat': resp['format']['type'],
            'team1': {
                'teamId': resp['team1']['id'],
                'teamName': resp['team1']['name'],
                'winner': resp['winnerTeam']['id'] == resp['team1']['id'],
                'score': len(list(filter(lambda x: 'result' in x and x['result']['team1TotalRounds'] > x['result']['team2TotalRounds'], resp['maps']))),
                'players': [player['name'] for player in resp['players']['team1']]
            },
            'team2': {
                'teamId': resp['team2']['id'],
                'teamName': resp['team2']['name'],
                'winner': resp['winnerTeam']['id'] == resp['team2']['id'],
                'score': len(list(filter(lambda x: 'result' in x and x['result']['team1TotalRounds'] < x['result']['team2TotalRounds'], resp['maps']))),
                'players': [player['name'] for player in resp['players']['team2']]
            }
        })

        self.ptr += 1
        time.sleep(0.5)

        return matchInfo
