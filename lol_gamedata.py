import time
import requests
import pandas as pd
from tqdm import tqdm
from random import sample
import random


def set_api_key(s):
    global api_key
    api_key = s


def get_puuid(gameid):
    url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/" + gameid + "?api_key=" + api_key
    res = requests.get(url).json()
    puuid = res['puuid']
    return puuid


def get_list_of_matchIds(puuid: str, count: int) -> list:
    url2 = 'https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/' + puuid + "/ids?start=0&count=" + str(
        count) + "&api_key=" + api_key
    res2 = requests.get(url2).json()
    lst = list(res2)
    return lst


def get_matches_timelines(match_ids):
    lst = []
    for s in tqdm(match_ids):
        url3 = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + s + '?api_key=' + api_key
        res3 = requests.get(url3).json()
        url4 = 'https://asia.api.riotgames.com/lol/match/v5/matches/' + s + '/timeline?api_key=' + api_key
        res4 = requests.get(url4).json()
        lst.append([s, res3, res4])
    return lst


def get_rawData(tier):
    div_list = ['I', 'II', 'III', 'IV']
    lst = []
    page_no = random.randrange(1, 10)

    for d in tqdm(div_list):
        url2 = 'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + '/' + d + '?page=' + \
               str(page_no) + '&api_key=' + api_key
        res2 = requests.get(url2).json()
        lst += sample(res2, 5)

    # riot api -> summonerName 가져오기
    lst_dia = [x['summonerName'] for x in lst]

    lst2 = []
    for s in tqdm(lst_dia[:5]):
        # summonerName을 통해서 puuid 가져오기
        try:
            puuid3 = get_puuid(s)
        except Exception as e:
            print(e)

    # match_ids 가져오기
    match_ids = get_list_of_matchIds(puuid3, 3)

    matches_timeline_list = get_matches_timelines(match_ids)

    # match.timeline 원시데이터 df 만들기
    df = pd.DataFrame(matches_timeline_list, columns=['match_id', 'matches', 'timeline'])
    return df


