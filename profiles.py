import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from collections import Counter
from math import pi

#tags are obtained from print_unique_tags in exploration.py
#group genres for Yee map
YEE_MAP = {
    'Action': ['action', 'ação', 'экшены', 'azione', '动作', '액션'],
    'Immersion': ['rpg', 'adventure', 'aventura', 'приключенческие игры', 'gdr', 'ролевые игры', '어드벤처'],
    'Social': ['multi-player', 'multijogador', 'online co-op', 'кооператив', 'co-op', 'multigiocatore','для нескольких игроков', '多人', '멀티플레이어', '协同作战', '远程同乐'],
    'Achievement': ['steam achievements', 'conquistas steam', 'достижения steam', 'achievement di steam','logros de steam', 'steam 도전 과제'],
    'Creativity': ['simulation', 'sandbox', 'game development', 'includes level editor', 'inclui editor de níveis','includes source sdk', 'incluye editor de niveles', 'incluye el sdk de source', 'workshop di steam',
        'steam 창작마당', '게임 개발', '게임 개발', '设计和插画'],
    'Strategy': ['strategy', 'стратегии', 'simulação', 'management', 'strategia']
}



#group genres for Bartle map
BARTLE_MAP = {
    'Killer': ['pvp', 'jvj', 'lan pvp', 'pvp in lan', 'shooter', 'battle royale', 'competitive', 'игрок против игрока', 'pvp online', '玩家对战', '线上玩家对战'],
    'Achiever': ['steam achievements', 'difficult', 'story rich', 'достижения steam', 'logros de steam', 'achievement di steam', 'steam 도전 과제'],
    'Explorer': ['adventure', 'open world', 'exploration', 'приключенческие игры', 'simulazione', '어드벤처'],
    'Socializer': ['multi-player', 'online co-op', 'co-op', 'shared/split screen', 'remote play together', 'кооператив', 'multijogador', 'multigiocatore', 'для нескольких игроков', '멀티플레이어', '远程同乐', '协同作战']
}


# ------------------- FUNCTIONS -------------------

def count_motivation_points(row, map_dict):
    #initializes a dictionary with all the points at 0.0
    count = {k: 0.0 for k in map_dict.keys()}
    #gets hours played for the row , default = 0
    weight = float(row.get('playtime_hours', 0))
    #gets achievements ratio
    achievements = float(row.get('achievement_ratio', 0))

    tags = []
    #iterates fot the clolumns genres and categories
    for col in ('genres', 'categories'):
        #gets value, default = empty
        cell = row.get(col, [])
        #if is a string
        if isinstance(cell, str):
            try:
                import ast
                #convert to list
                cell = ast.literal_eval(cell)
            except:
                cell = []
        for tag in cell:
            #add tag to list without spaces and in lowercase
            tags.append(tag.strip().lower())

    #for each motivation and keyword
    for motive, keywords in map_dict.items():
        for kw in keywords:
            kw = kw.strip().lower()
            #if a tag contains the keyword (kw)
            if any(kw in tag for tag in tags):
                #for achiever motivation multiplies by the obtained ratio
                if motive.lower() in ['achievement', 'achiever']:
                    count[motive] += weight * achievements
                else:
                    count[motive] += weight
                break

    return pd.Series(count)




def compute_profiles(df):
    #groups by participant id and uses count_motivation_points for each group for Yee
    yee_df = df.groupby('participant_id', group_keys=False).apply(
        lambda group: group.apply(count_motivation_points, axis=1, args=(YEE_MAP,)).sum()
    )
    #groups by participant id and uses count_motivation_points for each group for Bartle
    bartle_df = df.groupby('participant_id', group_keys=False).apply(
        lambda group: group.apply(count_motivation_points, axis=1, args=(BARTLE_MAP,)).sum()
    )

    return yee_df, bartle_df



# ------------------- VISUALIZATIONS -------------------



def save_yee_radar_png(yee_df, player_id, output_dir="output"):

    print(f"Generando yee para {player_id}")
    os.makedirs(output_dir, exist_ok=True)

    #normalizes values
    yee_normalized = yee_df.div(yee_df.sum(axis=1), axis=0)
    player_values = yee_normalized.loc[player_id].values
    #calculates average values for the group
    avg_values = yee_normalized.mean().values

    #get labels
    labels = list(yee_df.columns)
    #count variales
    num_vars = len(labels)

    #calculates angles for each variable
    angles = [n / float(num_vars) * 2 * pi for n in range(num_vars)]
    player_values = np.append(player_values, player_values[0])
    avg_values = np.append(avg_values, avg_values[0])
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    #player draw
    ax.plot(angles, player_values, linewidth=1.5, linestyle='solid', label=player_id)
    ax.fill(angles, player_values, alpha=0.3)

    #avg draw
    ax.plot(angles, avg_values, linewidth=1.5, linestyle='dashed', label='Grupo promedio')
    ax.fill(angles, avg_values, alpha=0.1)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_title(f"Gamer Motivation Profile - {player_id}")
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15))
    
    #save
    filename = f"{player_id}_gmp_yee.png"
    path = os.path.join(output_dir, filename)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()
    print(f"Creado") #confirmation
    
    
    #print punctuations
    print("Puntuaciones normalizadas Yee:") #users
    for label, val in zip(labels, yee_normalized.loc[player_id]):
        print(f"- {label}: {val:.2f}")
    print("Media del grupo:") #avg
    for label, val in zip(labels, yee_normalized.mean()):
        print(f"- {label}: {val:.2f}")
    print("==========================================")



def plot_bartle_compass(bartle_df, normalize=True, save_path="output/bartle_compass.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    x = bartle_df['Killer'] - bartle_df['Socializer']   #axis x action vs interaction
    y = bartle_df['Achiever'] - bartle_df['Explorer']   #axis y world vs players

    #normalize values
    if normalize:
        x = x / (np.abs(x).max() or 1)
        y = y / (np.abs(y).max() or 1)

    plt.figure(figsize=(10, 10))
    
    #point position for every participant
    for user in bartle_df.index:
        plt.scatter(x[user], y[user], s=100)
        plt.text(x[user] + 0.03, y[user] + 0.03, user, fontsize=10)

    #axis
    plt.axhline(0, color='black', linestyle='-', alpha=0.3)
    plt.axvline(0, color='black', linestyle='-', alpha=0.3)
    #dimensions
    plt.text(1.1, 1.1, 'Achiever', ha='center', va='center', fontsize=12, fontweight='bold', color='blue')
    plt.text(-1.1, 1.1, 'Explorer', ha='center', va='center', fontsize=12, fontweight='bold', color='green')
    plt.text(1.1, -1.1, 'Killer', ha='center', va='center', fontsize=12, fontweight='bold', color='red')
    plt.text(-1.1, -1.1, 'Socializer', ha='center', va='center', fontsize=12, fontweight='bold', color='purple')
    #axis labels
    plt.text(0, 1.15, 'MUNDO', ha='center', va='center', fontsize=11, fontweight='bold')
    plt.text(0, -1.15, 'JUGADORES', ha='center', va='center', fontsize=11, fontweight='bold')
    plt.text(1.15, 0, 'ACCIÓN', ha='center', va='center', fontsize=11, fontweight='bold', rotation=90)
    plt.text(-1.15, 0, 'INTERACCIÓN', ha='center', va='center', fontsize=11, fontweight='bold', rotation=270)

    plt.xlim(-1.3, 1.3)
    plt.ylim(-1.3, 1.3)
    plt.title('Taxonomía de Bartle', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)

    #save
    plt.tight_layout()
    plt.savefig(save_path, format='png')
    plt.close()

    #confirmation
    print("Bartle creado")

    #group resume
    print("\nResumen grupal:")
    print(f"→ Eje X: media = {x.mean():+.2f} | mediana = {x.median():+.2f}")
    print(f"→ Eje Y: media = {y.mean():+.2f} | mediana = {y.median():+.2f}")
    print("==========================================")



#TOP games and genres
def plot_top_games_with_genres(df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    users = df['participant_id'].unique()
    
    for user_id in users:
        print(f"Creando para {user_id}")
        
        try:
            user_data = df[df['participant_id'] == user_id]
            top_games = user_data.nlargest(10, 'playtime_hours') #TOP 10 games
            
            #if no data for user
            if len(top_games) == 0:
                print(f"Error datos {user_id}")
                continue
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
            
            ####playtime graph
            bars1 = ax1.barh(range(len(top_games)), top_games['playtime_hours'], 
                             color='skyblue', alpha=0.7)
            ax1.set_yticks(range(len(top_games)))
            
            #reduce long names
            formatted_names = []
            for name in top_games['name_x']:
                    name_str = str(name)
                    if len(name_str) > 30:
                        formatted_names.append(name_str[:20] + '...')
                    else:
                        formatted_names.append(name_str)
            
            ax1.set_yticklabels(formatted_names, fontsize=14)
            ax1.set_xlabel('Horas jugadas', fontsize=14)
            ax1.set_title(f'Top 10 juegos más jugados - {user_id}', fontsize=18)
            
            #add values
            for i, v in enumerate(top_games['playtime_hours']):
                ax1.text(v + 0.5, i, f'{v:.1f}h', va='center', fontsize=12)
            
            ####genres graph
            all_genres = []
            for genres in top_games['genres']:
                if pd.isna(genres):
                    continue
                elif isinstance(genres, list):
                    all_genres.extend(genres)
                elif isinstance(genres, str) and genres:
                    try:
                        import ast
                        genres_list = ast.literal_eval(genres)
                        if isinstance(genres_list, list):
                            all_genres.extend(genres_list)
                        else:
                            all_genres.append(str(genres_list))
                    except:
                        all_genres.append(genres)
            
            genre_counts = Counter(all_genres)
            top_genres = dict(genre_counts.most_common(8)) #TOP 8 genres
            
            if top_genres:
                ax2.bar(range(len(top_genres)), list(top_genres.values()), 
                        color='lightcoral', alpha=0.7)
                ax2.set_xticks(range(len(top_genres)))
                ax2.set_xticklabels(list(top_genres.keys()), rotation=45, ha='right', fontsize=14)
                ax2.set_ylabel('Frecuencia', fontsize=14)
                ax2.set_title(f'Géneros dominantes en juegos más jugados - {user_id}', fontsize=18)
            else:
                #if no data
                ax2.text(0.5, 0.5, 'Sin datos disponibles', 
                        ha='center', va='center', transform=ax2.transAxes)
                ax2.set_title(f'Géneros dominantes - {user_id}')
            
            plt.tight_layout()
            
            #save
            filename = f"{user_id}_games_and_genres.png"
            path = os.path.join(output_dir, filename)
            plt.savefig(path, dpi=600, bbox_inches='tight')
            plt.close()
            
            #confirmation for individual user
            print(f"Creado para {user_id}")
            
        except Exception as e:
            print(f"Error en {user_id}")
            continue
    #confirmation for all users
    print(f"Creado para todos los usuarios")


#genre distribution
def plot_genre_distribution_histogram(df, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    
    users = df['participant_id'].unique()
    
    for user_id in users:
        print(f"Creando para {user_id}")
        
        try:
            user_data = df[df['participant_id'] == user_id]
            
            #extraer generos
            all_genres = []
            for genres in user_data['genres']:
                if pd.isna(genres):
                    continue
                elif isinstance(genres, list):
                    all_genres.extend(genres)
                elif isinstance(genres, str) and genres:
                    try:
                        import ast
                        genres_list = ast.literal_eval(genres)
                        if isinstance(genres_list, list):
                            all_genres.extend(genres_list)
                        else:
                            all_genres.append(str(genres_list))
                    except:
                        all_genres.append(genres)
            
            if not all_genres:
                print(f"No hay géneros para {user_id}")
                continue
            
            genre_counts = Counter(all_genres)
            top_genres = dict(genre_counts.most_common(10)) #TOP 10
            
            #create graph
            plt.figure(figsize=(12, 6))
            bars = plt.bar(range(len(top_genres)), list(top_genres.values()), 
                           color='steelblue', alpha=0.7)
            
            plt.xticks(range(len(top_genres)), list(top_genres.keys()), 
                       rotation=45, ha='right', fontsize=14)
            plt.ylabel('Número de juegos')
            plt.title(f'Distribución de géneros en la biblioteca - {user_id}', fontsize=18, fontweight='bold')
            
            #add values on the bars
            for bar, value in zip(bars, top_genres.values()):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                        str(value), ha='center', va='bottom', fontsize=12)
            
            plt.tight_layout()
            
            #save in local
            filename = f"{user_id}_genre_histogram.png"
            path = os.path.join(output_dir, filename)
            plt.savefig(path, dpi=600, bbox_inches='tight')
            plt.close()
            
            print(f"Creado para {user_id}")
            
        except Exception as e:
            print(f"Error en {user_id}")
            continue
    #confirmation
    print(f"Creado para todos los usuarios")


# ------------------- PROFILE REPORT -------------------


def print_user_stats(df):
    participants = df['participant_id'].unique()

    #for each user and played games
    for user in sorted(participants):
        user_df = df[df['participant_id'] == user]
        played_games = user_df[user_df['playtime_hours'] > 0]

        #calculates
        total_games = len(user_df) #number of games
        num_played = len(played_games) #number of played games
        total_playtime = played_games['playtime_hours'].sum() #total playtime
        avg_playtime = played_games['playtime_hours'].mean() #average playtime hours
        median_playtime = played_games['playtime_hours'].median() #playtime median

        #achievemnts ratio
        played_with_achievements = played_games[played_games['achievement_ratio'].notna()]
        mean_achievement_ratio = played_with_achievements['achievement_ratio'].mean()

        #report
        print(f"Resultados para {user}") #user
        print(f"- Juegos en la biblioteca: {total_games}") #number of games
        print(f"- Juegos jugados: {num_played}") #number of played games
        print(f"- Porcentaje jugados: {num_played / total_games:.1%}") #percentaje of played games
        print(f"- Tiempo total jugado: {total_playtime:.1f} h") #total playtime
        print(f"- Tiempo medio por juego: {avg_playtime:.1f} h") #average playtime hours
        print(f"- Mediana de horas jugadas: {median_playtime:.1f} h") #median playtime
        print(f"- Ratio medio de logros (juegos jugados): {mean_achievement_ratio:.2f}") #achievemnts ratio
        print("========================================")



