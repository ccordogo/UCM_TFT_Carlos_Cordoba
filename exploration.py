import ast  #para convertir string a lista

import pandas as pd

def to_list_if_str(x):
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except:
            return []
    return x

def print_unique_tags(df):
    all_genres = set()
    all_categories = set()

    df['genres'] = df['genres'].apply(to_list_if_str)
    df['categories'] = df['categories'].apply(to_list_if_str)

    for genres in df['genres']:
        all_genres.update(genres)

    for categories in df['categories']:
        all_categories.update(categories)

    print("Géneros:")
    for genre in sorted(all_genres):
        print(f" - {genre}")

    print("Categorías:")
    for cat in sorted(all_categories):
        print(f" - {cat}")

