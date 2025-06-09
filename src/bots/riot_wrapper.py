import requests
import datetime
import textwrap
import collections
from helpers import *

try:
    RIOT_API_KEY = read_section_secret('riot', 'api_key')
    WEBHOOK_URL = read_section_secret('riot', 'webhook_url')
    RIOT_IDS = read_section_secret('riot', 'riot_ids')
    USER_REGION = read_section_secret('riot', 'user_region')
    WIDE_REGION = read_section_secret('riot', 'wide_region')
except KeyError as e:
    print(e, "must be specified in config [riot] section")
    exit(1)

user_in_game = collections.defaultdict(dict)

class riot_wrapper():
    def __init__(self):
        for id in RIOT_IDS:
            set_value(user_in_game, id, 'previous_game', '')
            set_value(user_in_game, id, 'last_match', '')
            
    def get_account_dtos():
        accounts = []
        for id in RIOT_IDS:
            separator_index = id.find('#')
            name = id[:separator_index]
            tag = id[separator_index + 1:]
            account_url = f"https://{WIDE_REGION}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            response = requests.get(account_url, headers={'X-Riot-Token': RIOT_API_KEY})
            
            if not response.ok:
                raise Exception("Could not get account", response)
            accounts.append(response.json())
        return accounts
    
    def get_summoner_dto(account_dto):
        puuid = account_dto['puuid']
        summoner_by_puuid_url = f"https://{USER_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
        response = requests.get(summoner_by_puuid_url, headers={'X-Riot-Token': RIOT_API_KEY})
        summoner_dto = response.json()
        
        if not response.ok:
            raise Exception("Could not get summoner", summoner_dto)
        return summoner_dto
    
    def get_active_game(account, summoner):
        puuid = summoner['puuid']
        username = f"**{account['gameName']}** #{account['tagLine']}"
        
        active_games_url = f"https://{USER_REGION}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
        response = requests.get(active_games_url, headers={'X-Riot-Token': RIOT_API_KEY})
        current_game_info = response.json()
        
        if response.status_code == 404 : return
        if not response.ok : raise Exception("Could not get active game", current_game_info)
        
        current_game = str(current_game_info['gameId'])
        previous_game = get_value(user_in_game, puuid, 'previous_game')
        if previous_game == current_game : return
        
        current_game = str(current_game_info['gameId'])
        today = datetime.datetime.now()
        midnight = datetime.datetime(today.year, today.month, today.day, tzinfo=datetime.timezone.utc)
        midnight_epoch = int(midnight.timestamp())
        day_ago = today - datetime.timedelta(days=1)
        day_ago_epoch = int(day_ago.timestamp())
        
        matches_by_puuid_url = f"https://{WIDE_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(matches_by_puuid_url, params={'startTime': midnight_epoch}, headers={'X-Riot-Token': RIOT_API_KEY})
        matches_dto = response.json()
        
        if not response.ok : raise Exception("Could not get match history", matches_dto)
        matches_today = len(matches_dto)
        
        response = requests.get(matches_by_puuid_url, params={'startTime': day_ago_epoch}, headers={'X-Riot-Token': RIOT_API_KEY})
        matches_dto = response.json()
        
        if not response.ok : raise Exception("Could not get match history", matches_dto)
        matches_past_24h = len(matches_dto)
        
        message = f"{username} started a new game (ID: {current_game})"
        print(message)
        
        # user_in_game[str(puuid)]['previous_game'] = str(current_game)
        set_value(user_in_game, puuid, 'previous_game', str(current_game))
        return {
            "title": username,
                "description": textwrap.dedent(
                    f"""
                    Started a new game :sparkles:
                    
                    It's their {add_ordinal_suffix(matches_today + 1)} game today,
                    {add_ordinal_suffix(matches_past_24h + 1)} game in the past 24h
                    
                    ID: {current_game}
                    """
                ),
                "color": 16738740,
        }
        
    def get_game_result(account, summoner):
        puuid = summoner['puuid']
        username = f"**{account['gameName']}** #{account['tagLine']}"
        summoner_eid = summoner['id']
        last_match = get_value(user_in_game, puuid, 'last_match')
        
        matches_by_puuid_url = f"https://{WIDE_REGION}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        response = requests.get(matches_by_puuid_url, params={'count': 1}, headers={'X-Riot-Token': RIOT_API_KEY})
        matches_dto = response.json()
        
        if not response.ok : raise Exception("Could not get match history", matches_dto)
        if not matches_dto : return
        
        match = matches_dto[0]
        if match == last_match : return
        
        match_by_id_url = f"https://{WIDE_REGION}.api.riotgames.com/lol/match/v5/matches/{match}"
        response = requests.get(match_by_id_url, headers={'X-Riot-Token': RIOT_API_KEY})
        match_dto = response.json()
        if not response.ok : raise Exception("Could not get match details", match_dto)
        
        rank_message = ""
        queue_id = match_dto['info']['queueId']

        queue_dict = {
            420: {
                'type': 'RANKED_SOLO_5x5',
                'str': "SOLO/DUO",
            },
            440: {
                'type': 'RANKED_FLEX_SR',
                'str': "FLEX",
            },
            450: {
                'type': 'ARAM',
                'str': "ARAM",
            },
            1700: {
                'type': 'CHERRY',
                'str': "ARENA",
            },
        }
        
        if queue_id in queue_dict:
            queue_str = queue_dict[queue_id]['str']
            queue_type = queue_dict[queue_id]['type']

            rank_message = f"\n\n{queue_str}"

            league_entries_url = f"https://{USER_REGION}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_eid}"
            response = requests.get(league_entries_url, headers={'X-Riot-Token': RIOT_API_KEY})
            league_entries = response.json()
            if not response.ok : raise Exception("Could not get league entries", league_entries)

            for entry in league_entries:
                if entry['queueType'] == queue_type:
                    try:
                        if entry['tier'] in ['MASTER', 'GRANDMASTER', 'CHALLENGER']:
                            rank_message += f"\n{entry['tier']} {entry['leaguePoints']}LP"
                        else:
                            rank_message += f"\n{entry['tier']} {entry['rank']} {entry['leaguePoints']}LP"
                    except KeyError:
                        pass

                    try:
                        wins = entry['wins']
                        losses = entry['losses']
                        total = 100 * wins / (wins + losses)
                        rank_message += f"\n{wins}W {losses}L {total:.2f}% WR"
                    except KeyError:
                        pass
            
            participants = match_dto['info']['participants']
            numeric_id = match.split("_")[1]
            
            duration_multiplier = 1000 if 'gameEndTimestamp' not in match_dto['info'] else 1
            if match_dto['info']['gameDuration'] <= 5 * 60 * duration_multiplier:
                # game lasted less than 5 minutes - likely a remake
                response = requests.post(WEBHOOK_URL, json={'embeds': [
                    {
                        "title": username,
                        "description": f"remake...\nID:{numeric_id}",
                        "color": 8421504
                    },
                ]})
                if not response.ok:
                    raise Exception("Could not post to Discord")
            else:
                for p in participants:
                    if p['puuid'] == puuid:
                        emoji = ":trophy:" if p['win'] else ":poop:"
                        result = "WON" if p['win'] else "LOST"
                        color = 44197 if p['win'] else 15232903
                        print(f"{result} (ID: {numeric_id})")

                        placement = ''
                        if p.get('placement', 0) != 0:
                            placement = f"{add_ordinal_suffix(p['placement'])} place\n\nID: {numeric_id}"

                        set_value(user_in_game, puuid, 'last_match', str(matches_dto[0]))
                        return {
                            "title": username,
                                "description": f"{placement} {result} {emoji}{rank_message}",
                                "color": color,
                        }
                        
        # set_value(user_in_game, puuid, 'last_match', str(matches_dto[0]))