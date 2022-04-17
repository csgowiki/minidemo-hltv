# -*- coding: utf-8 -*-

from pydantic import BaseModel

# result for 1 map
class TeamResult(BaseModel):
    teamId: int
    teamName: str
    winner: bool
    score: int
    players: list = [] # [playerName]
    ctRounds: list = [] # [int]

# only for 1 map
class MatchInfo(BaseModel):
    matchId: int
    demoLink: str
    timestamp: int
    date: str
    eventName: str
    mformat: str      # match format
    team1: TeamResult
    team2: TeamResult
    maxround: int = 0

class MatchMapInfo(BaseModel):
    mapName: str
    matchInfo: MatchInfo