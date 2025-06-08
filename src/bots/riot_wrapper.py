import requests
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