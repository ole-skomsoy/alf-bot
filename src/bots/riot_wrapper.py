import requests
import datetime
import textwrap
from helpers import *

try:
    RIOT_API_KEY = read_section_secret('riot', 'api_key')
    WEBHOOK_URL = read_section_secret('riot', 'webhook_url')
    RIOT_IDS = read_section_secret('riot', 'riot_ids')
    USER_REGION = read_section_secret('riot', 'user_region')
    WIDE_REGION = read_section_secret('riot', 'wide_region')
    DATA_FILE = read_section_secret('riot', 'data_file')
except KeyError as e:
    print(e, "must be specified in config [riot] section")
    exit(1)

class riot_wrapper():
    def get_account_dtos():
        accounts = []
        for id in RIOT_IDS:
            separator_index = id.find('#')
            name = id[:separator_index]
            tag = id[separator_index + 1:]
            account_url = f"https://{WIDE_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            response = requests.get(account_url, headers={'X-Riot-Token': RIOT_API_KEY}).json()
            
            if not response:
                raise Exception("Could not get account", response)
            accounts.append(response)
        return accounts
    
    def get_summoner_dto(account_dto):
        puuid = account_dto['puuid']
        summoner_by_puuid_url = f"https://{USER_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(summoner_by_puuid_url, headers={'X-Riot-Token': RIOT_API_KEY})
        summoner_dto = response.json()
        
        if not response:
            raise Exception("Could not get summoner", summoner_dto)
        return summoner_dto
    
    def get_active_game(account, summoner, data):
        puuid = summoner['puuid']
        username = f"**{account['gameName']}** #{account['tagLine']}"
        active_games_url = f"https://{USER_REGION}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
        response = requests.get(active_games_url, headers={'X-Riot-Token': RIOT_API_KEY})
        current_game_info = response.json()
        
        if response.status_code == 404:
            print("Currently not in game")
            return
        if not response:
            raise Exception("Could not get active game", current_game_info)
        
        current_game = str(current_game_info['gameId'])
        previous_game = data['in_game']
        if previous_game == current_game:
            print(f"In the same game (ID: {current_game})")
            return
        
        today = datetime.datetime.now()
        midnight = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.timezone.utc)
        midnight_epoch = int(midnight.timestamp())
        day_ago = today - datetime.timedelta(days=1)
        day_ago_epoch = int(day_ago.timestamp())
        
        matches_by_puuid_url = f"https://{WIDE_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(matches_by_puuid_url, params={'startTime': midnight_epoch}, headers={'X-Riot-Token': RIOT_API_KEY})
        matches_dto = response.json()
        
        if not response:
            raise Exception("Could not get match history", matches_dto)
        matches_today = len(matches_dto)
        
        response = requests.get(matches_by_puuid_url, params={'startTime': day_ago_epoch}, headers={'X-Riot-Token': RIOT_API_KEY})
        matches_dto = response.json()
        if not response:
            raise Exception("Could not get match history", matches_dto)
        matches_past_24h = len(matches_dto)
        
        message = f"{username} started a new game (ID: {current_game})"
        data['in_game'] = str(current_game)
        print(message)
        
        return {'embeds': [
            {
                "title": username,
                "description": textwrap.dedent(
                    f"""
                    started a new game :sparkles:
                    
                    it's their {add_ordinal_suffix(matches_today + 1)} game today,
                    {add_ordinal_suffix(matches_past_24h + 1)} game in the past 24h
                    """
                ),
                "color": 16738740,
                "footer": {
                    "text": f"ID: {current_game}"
                },
            },
        ]}