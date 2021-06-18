import difflib
import pandas as pd



def get_closest(name, state_names_list, prob):
    return difflib.get_close_matches(name, state_names_list, 1, 0.4)
    

def change_names_in_df(df, state_column, state_names_list, prob):
    df[state_column] = df[state_column].apply(lambda x: get_closest(x, state_names_list, prob))
    return df