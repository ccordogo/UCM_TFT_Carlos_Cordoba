from utils import normalize_list_column
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import numpy as np


#upload data from csv and sort by participant id
df = pd.read_csv("data/steam_data.csv")
df = df.sort_values(by='participant_id')

#convert genres and categories columns to lists
df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df['categories'] = df['categories'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# ------------------- TOP GENRES -------------------
#creates a row for every game genre
exploded_genres = df.explode('genres')
#group by genre and sort ny hours played, getting the TOP 10
top_genres = exploded_genres.groupby('genres')['playtime_hours'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_genres.values, y=top_genres.index, palette='Blues_r')
plt.title('Top 10 géneros más jugados por horas')
plt.xlabel('Horas jugadas')
plt.ylabel('Género')
plt.tight_layout()
#save as png
plt.savefig("output/top_generos_grupo.png")
plt.close()

# ------------------- TOP CATEGORIES -------------------
#creates a row for every game category
exploded_categories = df.explode('categories')
#group by genre and sort ny hours played, getting the TOP 10
top_categories = exploded_categories.groupby('categories')['playtime_hours'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_categories.values, y=top_categories.index, palette='Greens_r')
plt.title('Top 10 categorías más jugadas por horas')
plt.xlabel('Horas jugadas')
plt.ylabel('Categoría')
plt.tight_layout()
#save as png
plt.savefig("output/top_categorias_grupo.png")
plt.close()

# ------------------- COMPARATIVE HLTB ------------------- (HowLongToBeat)
#filter games with data from hltb with more than 0 hours
df_hltb = df[(df['hltb_main_story'].notna()) & (df['hltb_main_story'] > 0)]

plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=df_hltb,
    x='hltb_main_story',
    y='playtime_hours',
    hue='participant_id',
    alpha=0.7
)
plt.plot([0, 100], [0, 100], linestyle='--', color='grey')
plt.title('Horas jugadas vs estimación HLTB')
plt.xlabel('HLTB: Historia principal (horas)')
plt.ylabel('Horas jugadas reales')
plt.xlim(0, df_hltb['hltb_main_story'].max() + 5)
plt.ylim(0, df_hltb['playtime_hours'].max() + 5)
plt.savefig("output/plot_hltb.png")
plt.close()



# ------------------- COMPARATIVE HLTB (FILTERED) ------------------- #
#filter to games between HLTB in range [+0, 100] and playtime hours  in range [+0, 200]
df_hltb_filtered = df[
    (df['hltb_main_story'].notna()) &
    (df['hltb_main_story'] > 0) &
    (df['hltb_main_story'] <= 100) &
    (df['playtime_hours'] > 0) &  
    (df['playtime_hours'] <= 200)
]

plt.figure(figsize=(8, 6))
sns.scatterplot(
    data=df_hltb_filtered,
    x='hltb_main_story',
    y='playtime_hours',
    hue='participant_id',
    alpha=0.7
)
plt.plot([0, 100], [0, 100], linestyle='--', color='grey')
plt.title('Horas jugadas vs estimación HLTB (filtrado)')
plt.xlabel('HLTB: Historia principal (horas)')
plt.ylabel('Horas jugadas reales')
#axis limitations
plt.xlim(0, 105)
plt.ylim(0, 205)
plt.tight_layout()
plt.savefig("output/plot_hltb_filtered.png")
plt.close()




# ------------------- GENERAL INSIGHT -------------------
print("\nResumen exploratorio:")
print("- Número de juegos totales:", len(df)) #total number of games
print("- Número de juegos únicos:", df['appid'].nunique()) #total number of unique games
print("- Número de juegos compartidos:", len(df)-df['appid'].nunique()) #total number of repeated games
print("- Número de participantes:", df['participant_id'].nunique()) #number of participants
print("- Género más jugado:", top_genres.idxmax()) #most played genre
print("- Categoría más jugada:", top_categories.idxmax()) #most played category
print("- Tiempo medio por juego:", round(df['playtime_hours'].mean(), 2), "horas") #average game time

mean_played = df[df['playtime_hours'] > 0]['playtime_hours'].mean() #calculate mean
print("- Tiempo medio por juego (solo si jugado):", round(mean_played, 2), "horas") #average mean time for played games

num_juegos_0_horas = (df['playtime_hours'] == 0).sum() #calculate 0 hours played games
print("- Juegos con 0 horas jugadas:", num_juegos_0_horas) #games with 0 hours

num_juegos_jugados = df[df['playtime_hours'] > 0]['appid'].nunique() #calculate number of unique played games for more than 0 hours
print("- Número de juegos únicos con más de 0 horas:", num_juegos_jugados) #unique games with +0 hours


juegos_total = df['appid'].unique() #total unique games
juegos_jugados = df[df['playtime_hours'] > 0]['appid'].unique() #played unique games
juegos_no_jugados = set(juegos_total) - set(juegos_jugados) #unique not played games

print("- Número de juegos únicos con 0 horas:", len(juegos_no_jugados)) #unique games with 0 hours


# ------------------- Top 10 games -------------------


top_games_group = (
    df.groupby('name_x')['playtime_hours'] #group by game name
    .sum() #sum total hours
    .sort_values(ascending=False)
    .head(10) #get TOP 10
)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_games_group.values, y=top_games_group.index, palette="Oranges_d")
plt.title("Top 10 juegos más jugados por el grupo")
plt.xlabel("Horas totales jugadas")
plt.ylabel("Juego")
plt.tight_layout()
plt.savefig("output/top_juegos_grupo.png")
plt.close()


# ------------------- EDA -------------------
#filter only played games
played = df[df['playtime_hours'] > 0]['playtime_hours']

#dispersion statistics
std = played.std()
mean = played.mean()
cv = std / mean if mean != 0 else np.nan  #coefficient of variation
percentiles = played.quantile([0.25, 0.5, 0.75, 0.9])
iqr = percentiles[0.75] - percentiles[0.25] #interquartile range


#print statistics
print("----------------------Estadísticos--------------------------")
print(f"- Desviación estándar: {std:.2f} horas")
print(f"- Coeficiente de variación (CV): {cv:.2f}")
print(f"- Percentil 25 (Q1): {percentiles[0.25]:.2f} horas")
print(f"- Percentil 50 (Mediana): {percentiles[0.5]:.2f} horas")
print(f"- Percentil 75 (Q3): {percentiles[0.75]:.2f} horas")
print(f"- Percentil 90: {percentiles[0.9]:.2f} horas")
print(f"- Rango intercuartílico (IQR): {iqr:.2f} horas")





# ------------------- NO GENRE/CATEGORY -------------------
sin_genero = 0 #no genre
sin_categoria = 0 #no category

for i, row in df.iterrows():
    #count empty genre
    if not row['genres'] or row['genres'] == [] or row['genres'] == "['']":
        sin_genero += 1

    #count empty category
    if not row['categories'] or row['categories'] == [] or row['categories'] == "['']":
        sin_categoria += 1

print(f"Juegos sin género: {sin_genero}") #nbo genre
print(f"Juegos sin categoría: {sin_categoria}") #no category