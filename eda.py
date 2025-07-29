from utils import normalize_list_column
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import ast
import numpy as np

df = pd.read_csv("data/steam_data.csv")
df = df.sort_values(by='participant_id')


df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])
df['categories'] = df['categories'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else [])

# ------------------- TOP GÉNEROS -------------------
exploded_genres = df.explode('genres')
top_genres = exploded_genres.groupby('genres')['playtime_hours'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_genres.values, y=top_genres.index, palette='Blues_r')
plt.title('Top 10 géneros más jugados por horas')
plt.xlabel('Horas jugadas')
plt.ylabel('Género')
plt.tight_layout()
plt.savefig("output/top_generos_grupo.png")

# ------------------- TOP CATEGORÍAS -------------------
exploded_categories = df.explode('categories')
top_categories = exploded_categories.groupby('categories')['playtime_hours'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_categories.values, y=top_categories.index, palette='Greens_r')
plt.title('Top 10 categorías más jugadas por horas')
plt.xlabel('Horas jugadas')
plt.ylabel('Categoría')
plt.tight_layout()
plt.savefig("output/top_categorias_grupo.png")

# ------------------- COMPARATIVA HLTB -------------------
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
print("✅ Guardado: output/plot_hltb.png")


# ───── HORAS VS HLTB (FILTRADO) ───── #
import seaborn as sns
import matplotlib.pyplot as plt

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
plt.xlim(0, 105)
plt.ylim(0, 205)
plt.tight_layout()
plt.savefig("output/plot_hltb_filtered.png")
plt.close()
print("✅ Guardado: output/plot_hltb_filtered.png")



# ------------------- INSIGHT GENERAL -------------------
print("\nResumen exploratorio:")
print("- Número de juegos totales:", len(df))
print("- Número de juegos únicos:", df['appid'].nunique())
print("- Número de juegos compartidos:", len(df)-df['appid'].nunique())
print("- Número de participantes:", df['participant_id'].nunique())
print("- Género más jugado:", top_genres.idxmax())
print("- Categoría más jugada:", top_categories.idxmax())
print("- Tiempo medio por juego:", round(df['playtime_hours'].mean(), 2), "horas")

mean_played = df[df['playtime_hours'] > 0]['playtime_hours'].mean()
print("- Tiempo medio por juego (solo si jugado):", round(mean_played, 2), "horas")

num_juegos_0_horas = (df['playtime_hours'] == 0).sum()
print("- Juegos con 0 horas jugadas:", num_juegos_0_horas)

num_juegos_jugados = df[df['playtime_hours'] > 0]['appid'].nunique()
print("- Número de juegos únicos con más de 0 horas:", num_juegos_jugados)


juegos_total = df['appid'].unique()
juegos_jugados = df[df['playtime_hours'] > 0]['appid'].unique()
juegos_no_jugados = set(juegos_total) - set(juegos_jugados)

print("- Número de juegos únicos con 0 horas:", len(juegos_no_jugados))


#--------------------------Top 10 juegos ---------------------------------


top_games_group = (
    df.groupby('name_x')['playtime_hours']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))
sns.barplot(x=top_games_group.values, y=top_games_group.index, palette="Oranges_d")
plt.title("Top 10 juegos más jugados por el grupo")
plt.xlabel("Horas totales jugadas")
plt.ylabel("Juego")
plt.tight_layout()
plt.savefig("output/top_juegos_grupo.png")



#-----------------------------EDA--------------------------------


# Filtramos solo juegos jugados (> 0h)
played = df[df['playtime_hours'] > 0]['playtime_hours']

# Estadísticos de dispersión
std = played.std()
mean = played.mean()
cv = std / mean if mean != 0 else np.nan  # Coeficiente de variación
percentiles = played.quantile([0.25, 0.5, 0.75, 0.9])
iqr = percentiles[0.75] - percentiles[0.25]



print("----------------------Estadísticos--------------------------")
print(f"- Desviación estándar: {std:.2f} horas")
print(f"- Coeficiente de variación (CV): {cv:.2f}")
print(f"- Percentil 25 (Q1): {percentiles[0.25]:.2f} horas")
print(f"- Percentil 50 (Mediana): {percentiles[0.5]:.2f} horas")
print(f"- Percentil 75 (Q3): {percentiles[0.75]:.2f} horas")
print(f"- Percentil 90: {percentiles[0.9]:.2f} horas")
print(f"- Rango intercuartílico (IQR): {iqr:.2f} horas")





#-----------------------------SIN GÉNERO/CATEGORIA--------------------------------
sin_genero = 0
sin_categoria = 0

for i, row in df.iterrows():
    #contar genero vacio
    if not row['genres'] or row['genres'] == [] or row['genres'] == "['']":
        sin_genero += 1

    #contar categoria vacia
    if not row['categories'] or row['categories'] == [] or row['categories'] == "['']":
        sin_categoria += 1

print(f"Juegos sin género: {sin_genero}")
print(f"Juegos sin categoría: {sin_categoria}")