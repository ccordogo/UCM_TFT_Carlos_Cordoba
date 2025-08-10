import pandas as pd
import time

from participants import participants

from steam_api import get_owned_games_with_retry, get_game_metadata, get_achievement_ratio

from utils import normalize_list_column, convert_playtime_minutes_to_hours, add_hltb_data

all_data = []
metadata_list = []

#for every user name and id get games
for user_id, steam_id in participants.items():
    print(f"Descargando juegos para: {user_id}")
    games = get_owned_games_with_retry(steam_id)
    print(f"{user_id}: {len(games)} juegos encontrados") #number of games for user
    #if not games, continue to next user
    if not games:
        continue

    #creates dataframe with user id and converts playtime from minutes to hours
    df = pd.DataFrame(games)
    df['participant_id'] = user_id
    df = convert_playtime_minutes_to_hours(df)

    #achievements
    achievement_ratios = []
    #get achievement ratio for every game
    for appid in df['appid']:
        ratio = get_achievement_ratio(steam_id, appid)
        #if there is no value, return 0.0
        achievement_ratios.append(ratio if ratio is not None else 0.0)
        time.sleep(0.2)  #to avoid problems with the api
    #add column to df
    df['achievement_ratio'] = achievement_ratios
    all_data.append(df)

    #gets data of unique games
    for appid in df['appid'].unique():
        meta = get_game_metadata(appid)
        if meta:
            #creates dictionary
            metadata_list.append({
                "appid": appid,
                "name": meta.get("name", ""),
                "type": meta.get("type", ""),
                "genres": ", ".join([g["description"] for g in meta.get("genres", [])]) if "genres" in meta else "",
                "categories": ", ".join([c["description"] for c in meta.get("categories", [])]) if "categories" in meta else "",
                "release_date": meta.get("release_date", {}).get("date", ""),
                "developer": ", ".join(meta.get("developers", [])) if "developers" in meta else "",
                "publisher": ", ".join(meta.get("publishers", [])) if "publishers" in meta else ""
            })
        time.sleep(0.2)#to avoid problems with the api

#fuse df
df_all = pd.concat(all_data, ignore_index=True)
df_meta = pd.DataFrame(metadata_list)
#merge df with metadata
df_final = df_all.merge(df_meta, on="appid", how="left")

##normalize genres and categories
df_final['genres'] = normalize_list_column(df_final['genres'])
df_final['categories'] = normalize_list_column(df_final['categories'])

#remove duplicates
df_final = df_final.drop_duplicates(subset=['appid', 'participant_id'])

#add hltb (howlongtobeat) data
print(df_final.columns)
df_final = add_hltb_data(df_final, game_name_col='name_y')

#save csv
df_final.to_csv("data/steam_data.csv", index=False)
print("Datos guardados en data/steam_data.csv") #confirmation message
