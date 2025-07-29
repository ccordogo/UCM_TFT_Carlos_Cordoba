import pandas as pd
from profiles import compute_profiles

from profiles import plot_bartle_compass

from profiles import save_yee_radar_png

from profiles import print_user_stats

from profiles import plot_top_games_with_genres

from profiles import plot_genre_distribution_histogram

from exploration import print_unique_tags

#carga datos
df = pd.read_csv("data/steam_data.csv")

#calculo de los perfiles
yee_df, bartle_df = compute_profiles(df)


print_unique_tags(df)

plot_bartle_compass(bartle_df)

print("Jugadores:", list(yee_df.index))
for player in yee_df.index:
    save_yee_radar_png(yee_df, player)

print_user_stats(df)


plot_top_games_with_genres(df)
plot_genre_distribution_histogram(df)
    
print("Completado")