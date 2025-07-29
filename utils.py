import pandas as pd
from howlongtobeatpy import HowLongToBeat
import time

def normalize_list_column(series):
    return series.fillna('').apply(lambda x: [i.strip() for i in x.split(',')] if isinstance(x, str) else [])

def convert_playtime_minutes_to_hours(df):
    df['playtime_hours'] = (df['playtime_forever'] / 60).round(1)
    return df

def add_hltb_data(df, game_name_col='name'):
    hltb = HowLongToBeat()
    hltb_data = []

    game_names = df[game_name_col].dropna().unique()

    for name in game_names:
        try:
            results = hltb.search(name)
            if results:
                best_match = max(results, key=lambda x: x.similarity)
                hltb_data.append({
                    "name": best_match.game_name,
                    "hltb_main_story": best_match.main_story,
                    "hltb_main_extra": best_match.main_extra,
                    "hltb_completionist": best_match.completionist
                })
            else:
                hltb_data.append({
                    "name": name,
                    "hltb_main_story": None,
                    "hltb_main_extra": None,
                    "hltb_completionist": None
                })
            time.sleep(1.0)  # evita bloqueo api
        except Exception as e:
            print(f"Error con '{name}': {e}")
            hltb_data.append({
                "name": name,
                "hltb_main_story": None,
                "hltb_main_extra": None,
                "hltb_completionist": None
            })

    hltb_df = pd.DataFrame(hltb_data)

    #merge con columna pasada como argumento
    df = df.merge(hltb_df, left_on=game_name_col, right_on='name', how='left')

    return df
