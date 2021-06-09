import pandas as pd 
import geopandas as gpd
import plotly.graph_objects as go
import matplotlib.pyplot as plt 
import json
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
from sklearn.metrics import r2_score
from scipy import stats
population = pd.read_csv("population.txt").set_index("region")

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return r_value**2

def get_processed_region_frame(merged, region, future_lag, active_cutoff, slope_cutoff, increasing, start=None, end=None):
    
    regional_frame = merged[merged.region==region].reset_index(drop=True)
    
  
    if start is not None and end is not None:
        no_of_days = (datetime.strptime(end, '%Y-%m-%d') - datetime.strptime(start, '%Y-%m-%d')).days +1
        date_mask = (regional_frame['date'] >= start) & (regional_frame['date'] <= end)
        regional_frame = regional_frame.loc[date_mask].reset_index(drop=True)

    regional_frame["Active_7days"] = regional_frame.Active.rolling(7).apply(get_avg)/population.loc[region][0]

    regional_frame.loc[:,'fut_Active'] = 0
    for i in range(0, len(regional_frame)):
        if i+future_lag in regional_frame.index:
            regional_frame.loc[i, 'fut_Active'] = regional_frame.loc[i+future_lag, 'Active_7days']


    regional_frame['slope_increasing'] =  regional_frame.p_cliWHO_smooth_slope > regional_frame.p_cliWHO_smooth_slope.rolling(3).apply(get_last_avg)
    regional_frame['slope_decreasing'] =  regional_frame.p_cliWHO_smooth_slope < regional_frame.p_cliWHO_smooth_slope.rolling(3).apply(get_last_avg)
    if increasing ==True:
        regional_frame = regional_frame[ regional_frame["slope_increasing"] == True]
    elif increasing==False:
        regional_frame = regional_frame[ regional_frame["slope_decreasing"] == True]
        
    regional_frame = regional_frame[regional_frame["p_cliWHO_smooth_slope"] >= slope_cutoff ]
    regional_frame = regional_frame[ regional_frame["Active_7days"] >= active_cutoff ]
    regional_frame = regional_frame.dropna()
    return regional_frame.set_index("date")

def get_merged_df():
    df = pd.read_csv('IN-est.csv')
    df['date'] = pd.to_datetime(df['date'])  
    df = df.replace('Dadra and Nagar Haveli', 'Dadra & Nagar Haveli').replace('NCT of Delhi', 'Delhi')
    df = df.replace("Andaman and Nicobar", "Andaman and Nicobar Islands")
    df = df.replace("Daman and Diu", "Daman & Diu").replace("Dadra & Nagar Haveli", "Dadara & Nagar Havelli")
    df = df.rename(columns={'region_agg': 'region'})
    df_data = pd.read_csv('IN-data.csv')
    df_data['date'] = pd.to_datetime(df_data['date'])
    population = pd.read_csv("population.txt").set_index("region")
    merged = pd.merge(df, df_data,  how='left', left_on=['date','region'], right_on = ['date','region'])
    return merged
    
def get_avg(x):
    return sum(x) / len(x)

    
def get_last_avg(x):
    return sum(x[:-1]) / len(x[:-1])