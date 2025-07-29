import requests
from config import STEAM_API_KEY
import time

def get_owned_games(steam_id):
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "include_played_free_games": True,
        "format": "json"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('response', {}).get('games', [])
    except Exception as e:
        print(f"Error en obtención: {e}")
        return []


def get_owned_games_with_retry(steam_id, retries=3, delay=2):
    for attempt in range(retries):
        games = get_owned_games(steam_id)
        if games:  #si hay juegos, ok
            return games
        print(f"Intento {attempt+1} fallido")
        time.sleep(delay)
    print(f"Error en obtención tras {retries} intentos.")
    return []


def get_game_metadata(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data[str(appid)]['success']:
            return data[str(appid)]['data']
    return None


def get_achievement_ratio(steam_id, appid):
    #devuelve el ratio de logros desbloqueados (0-1)

    url = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "appid": appid,
        "l": "english"
    }
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json().get("playerstats", {})
    achs = data.get("achievements")
    if not achs:
        return None
    total = len(achs)
    unlocked = sum(a.get("achieved", 0) for a in achs)
    if total == 0:
        return None
    return unlocked / total
