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
    pageNo = random.randrange(1, 10)

    for d in tqdm(div_list):
        url2 = 'https://kr.api.riotgames.com/lol/league/v4/entries/RANKED_SOLO_5x5/' + tier + '/' + d + '?page=' + \
               str(pageNo) + '&api_key=' + api_key
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


def get_dataFrame(lst, n):
    lst2 = []
    for s in tqdm(lst[:n]):
        puuid3 = get_puuid(s)
        match_ids = get_list_of_matchIds(puuid3, 3)
        matches_timeline_list = get_matches_timelines(match_ids)
        lst2.extend(matches_timeline_list)
        # time.sleep(5.0)

    df = pd.DataFrame(lst2, columns=['match_id', 'matches', 'timeline'])
    return df


def get_summoner_Name_lst():
    url5 = 'https://kr.api.riotgames.com/lol/league/v4/grandmasterleagues/by-queue/RANKED_SOLO_5x5?api_key=' + api_key
    res = requests.get(url5).json()
    summoner_Name_lst = [s['summonerName'] for s in res['entries']]
    return summoner_Name_lst


def get_game_data(df):
    tmp_lst2 = []
    for h in tqdm(range(len(df))):
        for i in range(10):
            tmp_lst = [
                df.iloc[h].matches['info']['gameId'],
                df.iloc[h].matches['info']['participants'][i]['championName'],
                df.iloc[h].matches['info']['participants'][i]['kills'],
                df.iloc[h].matches['info']['participants'][i]['deaths'],
                df.iloc[h].matches['info']['participants'][i]['assists']
            ]
            tmp_lst2.append(tmp_lst)

    df2 = pd.DataFrame(tmp_lst2, columns=['gameId', 'championName', 'kills', 'deaths', 'assists'])

    return df2


def get_game_data_extended(df):
    tmp_lst2 = []
    for h in tqdm(range(len(df))):
        for i in range(10):
            info = df.iloc[h].matches['info']
            tmp_lst = [
                info['gameId'],
                info['gameDuration'],
                info['gameVersion'],
                info['participants'][i]['summonerName'],
                info['participants'][i]['summonerLevel'],
                info['participants'][i]['participantId'],
                info['participants'][i]['championName'],
                info['participants'][i]['champExperience'],
                info['participants'][i]['teamPosition'],
                info['participants'][i]['teamId'],
                info['participants'][i]['win'],
                info['participants'][i]['kills'],
                info['participants'][i]['deaths'],
                info['participants'][i]['assists'],
                info['participants'][i]['totalDamageDealtToChampions'],
                info['participants'][i]['totalDamageTaken']
            ]
            tmp_lst2.append(tmp_lst)

    df2 = pd.DataFrame(tmp_lst2, columns=['gameId', 'gameDuration', 'gameVersion', 'summonerName',
                                          'summonerLevel', 'participantId', 'championName',
                                          'champExperience', 'teamPosition', 'teamId', 'win',
                                          'kills', 'deaths', 'assists', 'totalDamageDealtToChampions',
                                          'totalDamageTaken'])
    return df2


def get_timeline_data(df):
    tmp_lst2 = []
    for h in tqdm(range(len(df))):
        for i in range(10):
            info = df.timeline[h]['info']
            tmp_lst = [
                info['gameId'],
                info['participants'][i]['participantId']
            ]
            for j in range(5, 26):
                try:
                    tmp_lst.append(info['frames'][j]['participantFrames'][str(i + 1)]['totalGold'])
                except:
                    tmp_lst.append(0)
            tmp_lst2.append(tmp_lst)

    df2 = pd.DataFrame(tmp_lst2, columns=['gameId', 'participantId', 'g_5', 'g_6', 'g_7', 'g_8', 'g_9', 'g_10', 'g_11',
                                          'g_12', 'g_13', 'g_14', 'g_15', 'g_16', 'g_17', 'g_18', 'g_19', 'g_20',
                                          'g_21', 'g_22', 'g_23', 'g_24', 'g_25'])

    return df2


def get_dataframe_from_game_data(df):
    tmp_lst2 = []
    for h in tqdm(range(len(df))):

        info1 = df.iloc[h].matches['info']
        info2 = df.timeline[h]['info']

        if info1['gameMode'] == 'CLASSIC':
            try:
                for i in range(10):
                    tmp_lst = [
                        info1['gameId'],
                        info1['gameDuration'],
                        info1['gameVersion'],
                        info1['participants'][i]['summonerName'],
                        info1['participants'][i]['summonerLevel'],
                        info1['participants'][i]['participantId'],
                        info1['participants'][i]['championName'],
                        info1['participants'][i]['champExperience'],
                        info1['participants'][i]['teamPosition'],
                        info1['participants'][i]['teamId'],
                        info1['participants'][i]['win'],
                        info1['participants'][i]['kills'],
                        info1['participants'][i]['deaths'],
                        info1['participants'][i]['assists'],
                        info1['participants'][i]['totalDamageDealtToChampions'],
                        info1['participants'][i]['totalDamageTaken'],
                    ]
                    for j in range(5, 26):
                        try:
                            tmp_lst.append(info2['frames'][j]['participantFrames'][str(i + 1)]['totalGold'])
                        except:
                            tmp_lst.append(0)
                    tmp_lst2.append(tmp_lst)
            except:
                continue

    df2 = pd.DataFrame(tmp_lst2, columns=['gameId', 'gameDuration', 'gameVersion', 'summonerName', 'summonerLevel',
                                          'participantId', 'championName', 'champExperience', 'teamPosition', 'teamId',
                                          'win', 'kills', 'deaths', 'assists', 'totalDamageDealtToChampions',
                                          'totalDamageTaken', 'g_5', 'g_6', 'g_7', 'g_8', 'g_9', 'g_10',
                                          'g_11', 'g_12', 'g_13', 'g_14', 'g_15', 'g_16', 'g_17', 'g_18',
                                          'g_19', 'g_20', 'g_21', 'g_22', 'g_23', 'g_24', 'g_25'])
    result_df = df2.drop_duplicates()
    print('complete! the number of df is %d' % len(df))
    return result_df


def get_df_with_mon(df):
    tmp_lst2 = []
    for h in tqdm(range(len(df))):

        info1 = df.iloc[h].matches['info']
        info2 = df.timeline[h]['info']

        if info1['gameMode'] == 'CLASSIC':
            try:
                for i in range(10):
                    tmp_lst = [
                        info1['gameId'],
                        info1['gameDuration'],
                        info1['gameVersion'],
                        info1['participants'][i]['summonerName'],
                        info1['participants'][i]['summonerLevel'],
                        info1['participants'][i]['participantId'],
                        info1['participants'][i]['championName'],
                        info1['participants'][i]['champExperience'],
                        info1['participants'][i]['teamPosition'],
                        info1['participants'][i]['teamId'],
                        info1['participants'][i]['win'],
                        info1['participants'][i]['kills'],
                        info1['participants'][i]['deaths'],
                        info1['participants'][i]['assists'],
                        info1['participants'][i]['totalDamageDealtToChampions'],
                        info1['participants'][i]['totalDamageTaken'],
                        info1['participants'][i]['baronKills'],
                        info1['participants'][i]['challenges']['teamElderDragonKills'],
                        info1['participants'][i]['dragonKills'],
                        info1['participants'][i]['challenges']['teamRiftHeraldKills']
                    ]
                    for j in range(5, 26):
                        try:
                            tmp_lst.append(info2['frames'][j]['participantFrames'][str(i + 1)]['totalGold'])
                        except:
                            tmp_lst.append(0)
                    tmp_lst2.append(tmp_lst)
            except:
                continue

    df2 = pd.DataFrame(tmp_lst2, columns=['gameId', 'gameDuration', 'gameVersion', 'summonerName', 'summonerLevel',
                                          'participantId', 'championName', 'champExperience', 'teamPosition', 'teamId',
                                          'win', 'kills', 'deaths', 'assists', 'totalDamageDealtToChampions',
                                          'totalDamageTaken', 'baronKills', 'teamElderDragonKills', 'dragonKills',
                                          'teamRiftHeraldKills',
                                          'g_5', 'g_6', 'g_7', 'g_8', 'g_9', 'g_10',
                                          'g_11', 'g_12', 'g_13', 'g_14', 'g_15', 'g_16', 'g_17', 'g_18',
                                          'g_19', 'g_20', 'g_21', 'g_22', 'g_23', 'g_24', 'g_25'])
    result_df = df2.drop_duplicates()
    print('complete! the number of df is %d' % len(df))
    return result_df


def make_df_building(raw_data):
    tmp = raw_data.copy()
    lst = []
    for i in range(len(tmp)):
        lst2 = []
        match = tmp.iloc[i].matches['info']
        timeline = tmp.iloc[i].timeline['info']

        tmp_list = list(map(lambda x: x['events'], timeline['frames']))
        evt_list = [e for arr in tmp_list for e in arr]
        rst_list = list(filter(lambda x: x['type'] == 'BUILDING_KILL', evt_list))

        laneType_list = list(map(lambda x: x['laneType'][:3], rst_list))
        teamId_list = list(map(lambda x: str(x['teamId']), rst_list))
        timestamp_list = list(map(lambda x: x['timestamp'], rst_list))
        first_key = laneType_list[0] + '|' + str(teamId_list[0])

        t_tmp = {}
        for k in range(len(laneType_list)):
            key_tmp = laneType_list[k] + '|' + teamId_list[k]
            if t_tmp.get(key_tmp) is None:
                t_tmp[key_tmp] = timestamp_list[k]

        for j in range(10):
            lst_tmp = []
            pts = match['participants'][j]
            lst_tmp.append(pts['teamPosition'])
            lst_tmp.append(pts['participantId'])
            key_tmp2 = lst_tmp[0][:3] + '|' + str(pts['teamId'])
            if t_tmp.get(key_tmp2):
                if key_tmp2 == first_key:
                    lst_tmp.append(1)
                else:
                    lst_tmp.append(0)  # if else 첫번째인지, 첫번째면 FirstTowerDT count +1

                lst_tmp.append(1)
                lst_tmp.append(t_tmp[key_tmp2])
            else:
                lst_tmp.append(0)
                lst_tmp.append(0)
                lst_tmp.append(0)
            lst2.append(lst_tmp)

        lst.append(lst2)

    return lst