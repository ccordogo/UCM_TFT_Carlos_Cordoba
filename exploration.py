import ast 

import pandas as pd

def to_list_if_str(x):
#converts strings to lists
    if isinstance(x, str):
        try:
            return ast.literal_eval(x)
        except:
            return []
    return x


def print_unique_tags(df):
    all_genres = set()
    all_categories = set()

    #uses previous function with genres and categories
    df['genres'] = df['genres'].apply(to_list_if_str)
    df['categories'] = df['categories'].apply(to_list_if_str)

    for genres in df['genres']:
        all_genres.update(genres)

    for categories in df['categories']:
        all_categories.update(categories)

    #print genre list
    print("Géneros:")
    for genre in sorted(all_genres):
        print(f" - {genre}")

    #print categories list
    print("Categorías:")
    for cat in sorted(all_categories):
        print(f" - {cat}")

