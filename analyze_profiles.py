import pandas as pd
from profiles import compute_profiles

from profiles import plot_bartle_compass

from profiles import save_yee_radar_png

from profiles import print_user_stats

from profiles import plot_top_games_with_genres

from profiles import plot_genre_distribution_histogram

from exploration import print_unique_tags

#upload data from csv
df = pd.read_csv("data/steam_data.csv")

#calculate profiles for yee and bartle
yee_df, bartle_df = compute_profiles(df)

#print the listed unique tags of the games
print_unique_tags(df)

#save bartle compass
plot_bartle_compass(bartle_df)

#save yee radar for each user
print("User:", list(yee_df.index))
for player in yee_df.index:
    save_yee_radar_png(yee_df, player)

#print stats for different users
print_user_stats(df)

#save top games and genres graph
plot_top_games_with_genres(df)
#save genre distribution grapg
plot_genre_distribution_histogram(df)

#print confirmation of the script end
print("Completed")