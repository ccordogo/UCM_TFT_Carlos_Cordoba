import requests
from config import STEAM_API_KEY
import time

#principal function
def get_owned_games(steam_id):
    #steam api endpoint
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    #dictionary with parameters we need from API
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }
    try:
        #get
        response = requests.get(url, params=params)
        #as json
        data = response.json()
        return data.get('response', {}).get('games', [])
    
    #exception handling
    except Exception as e:
        print(f"Error en obtención: {e}")
        return []


#sometimes steam api does not send the information in the first try
#so maybe its necessary to make multiple calls for each user
def get_owned_games_with_retry(steam_id, retries=3, delay=2):
    for attempt in range(retries):
        #using the function from before
        games = get_owned_games(steam_id)
        if games:  #if the call gets games, it return them directly
            return games
        print(f"Intento {attempt+1} fallido") #attempts control in errors
        #some error might happen because of private profiles settings on steam
        time.sleep(delay) #delay to avoid api problems

    #after the specified number of retries there are not games
    #prints error and empty list
    print(f"Error en obtención tras {retries} intentos.") 
    return []


#to obtain each game metadata
def get_game_metadata(appid):
    #endpoint for game information 
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    
    #api response handling
    response = requests.get(url)
    if response.status_code == 200:
        #converts to json
        data = response.json()
        if data[str(appid)]['success']: #verifies if success
            return data[str(appid)]['data']
    return None


#to get game achievement ratio [0, 1]
#achievements privacy settings may differ in users, not returning achievemnts information
def get_achievement_ratio(steam_id, appid):
    #
    url = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "appid": appid,
        "l": "english"
    }
    #response control
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    #get statistics
    data = resp.json().get("playerstats", {})
    achs = data.get("achievements")
    if not achs:
        return None
    #counts number of achievements and number of achieved (+1)
    total = len(achs)
    unlocked = sum(a.get("achieved", 0) for a in achs)
    if total == 0:
        return None
    return unlocked / total #ratio calculus
