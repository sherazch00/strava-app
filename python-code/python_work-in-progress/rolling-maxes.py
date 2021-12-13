# Rolling Maxes

# import libraries
import numpy as np
import pandas as pd

# prepare test activity dataframe
df_activity = pd.read_csv('../Golden-Cheetah/2021_02_05_15_59_07.csv') #Time Trial

df_activity = df_activity.drop(['nm', 'headwind', 'slope', 'temp', 'interval', 'lrbalance', 'lte', 'rte', 
              'lps', 'rps', 'smo2', 'thb', 'o2hb', 'hhb'], axis=1)


# add rolling means columns to dataframe
def rolling_means(df, col, durations):
    for d in durations:
        df[col+str(d)] = df[col].rolling(d, min_periods=d).mean()

durations = [1,5,15,30,60,120,300,600,1200,1800,3600,5400,7200]

rolling_means(df_activity, 'watts', durations)
rolling_means(df_activity, 'hr', durations)
rolling_means(df_activity, 'kph', durations)
rolling_means(df_activity, 'cad', durations)

# get max value in each rolling means columns
def rolling_max(df, col, durations):
    maxes = [['Field', 'Duration', 'Max', 'Start', 'End']]
    for d in durations:
        maxes.append([col, d, df[col+str(d)].max(), (df[col+str(d)].idxmax()-(d-1)), df[col+str(d)].idxmax()])
    return maxes

max_watts = rolling_max(df_activity, 'watts', durations)
max_hr = rolling_max(df_activity, 'hr', durations)
max_kph = rolling_max(df_activity, 'kph', durations)
max_cad = rolling_max(df_activity, 'cad', durations)

# print max watts, HR, speed, cadence over different time durations
print(max_watts[1:])
print(max_hr[1:])
print(max_kph[1:])
print(max_cad[1:])