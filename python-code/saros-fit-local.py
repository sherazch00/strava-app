#!/usr/bin/env python
# coding: utf-8
# ---
# # Download Activity Summary and Details from Strava
#
# Strava provides basic information on how to get access to the API at https://developers.strava.com/docs/getting-started/.  
# The information from the Strava API page combined with 
# https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde and other websites 
# allowed me to write the code necessary to connect to Strava.
#
# With some additional research I was able to download all my activities and their summary data.  Though, in all my online 
# searching I could not find any good examples of how to download all the detailed activity streams associated with each 
# Strava activity.  The code to download activity details was mostly written from scratch.
#
# **The value of this notebook is:**
#    - example of code to authenticate and connect to the Strava API (follow Strava instructions to create an app)
#    - download all activities and their associated summaries to a dataframe
#    - download all 11 detailed activity streams for each activity to a dataframe
#    - single notebook that authenticates to Strava, downloads activity summaries and downloads activity details
#
# **Additional useful features:**
#    - controls the number of requests so they don't exceed Strava's default limits (100 requests/15 min)
#    - stores all download activity details in pkl and csv format
#    - loads previously downloaded activity details and then only downloads details for new activities
#
# ###### NEXT STEPS:
#   - Create a separate notebook that loads the pkl file with activity details
#       - run basic analysis and create visualizations on the activity details
#       - run machine learning models on the activity details to find patterns in heartrate and wattage numbers
# ---
#
# **Written by:  Sheraz Choudhary**
# **Date:        November 2021**
# ---

# import libraries
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings

import numpy as np
import pandas as pd

import os
from os.path import join, dirname
import sys
import subprocess
import pathlib
from dotenv import load_dotenv

import codecs
from codecs import open
from datetime import date
import time  

# ## Connect to Strava -- Get Current Access Token
# (https://www.realpythonproject.com/3-ways-to-store-and-read-credentials-locally-in-python/)
credential_file = join(os.getcwd(), 'strava-credentials.env')

load_dotenv(credential_file)
client_id = os.environ.get('client_id')
client_secret = os.environ.get('client_secret')
refresh_token = os.environ.get('refresh_token')

# (https://github.com/franchyze923/Code_From_Tutorials/blob/master/Strava_Api/strava_api.py)
auth_url = "https://www.strava.com/oauth/token"

payload = {
    'client_id': client_id,
    'client_secret': client_secret,
    'refresh_token': refresh_token,
    'grant_type': "refresh_token",
    'f': 'json'
}

print("\nRequesting Token...")
res = requests.post(auth_url, data=payload, verify=False)
access_token = res.json()['access_token']
print("Access Token Received!")
print("")

# ## Create Dataframe with Summary Info for All Activities *(Strava API)*
# (http://www.hainke.ca/index.php/2018/08/23/using-the-strava-api-to-retrieve-activity-data/)
# Initialize the dataframe
activities_overview = pd.DataFrame()

url = "https://www.strava.com/api/v3/athlete/activities"
page = 1

while True:
    # get page of activities from Strava
    page_json = requests.get(url + '?access_token=' + access_token + '&per_page=200' + '&page=' + str(page)).json()

    for a in range(len(page_json)):
        # (https://stackoverflow.com/questions/21104592/)
        activity_json = pd.json_normalize(page_json[a])
        activities_overview = activities_overview.append(activity_json, ignore_index=True)

    # if no results then exit loop
    if (not page_json):
        break

    # increment page
    page += 1

# makes sense since new added on bottom
activities_overview = activities_overview.sort_values(by='id', ascending=True)

# activities_overview.tail(5)

print("Number of Strava Activities Found: ", activities_overview.shape)
print("")

activities_overview.to_csv('activities_overview.csv', header=True)
print("OVERVIEW CSV FILE UPDATED\n")


# ## Create Dataframe with DETAILED ACTIVITY DATA Streams for New Activities *(Strava API)*
# Streams Available via Strava API (https://developers.strava.com/docs/reference/#api-models-StreamSet)
# time....................TimeStream	An instance of TimeStream.
# distance................DistanceStream	An instance of DistanceStream.
# latlng..................LatLngStream	An instance of LatLngStream.
# altitude................AltitudeStream	An instance of AltitudeStream.
# velocity_smooth.........SmoothVelocityStream	An instance of SmoothVelocityStream.
# heartrate...............HeartrateStream	An instance of HeartrateStream.
# cadence.................CadenceStream	An instance of CadenceStream.
# watts...................PowerStream	An instance of PowerStream.
# temp....................TemperatureStream	An instance of TemperatureStream.
# moving..................MovingStream	An instance of MovingStream.
# grade_smooth............SmoothGradeStream	An instance of SmoothGradeStream.

# https://www.strava.com/api/v3/activities/4998708851/streams?access_token=######&keys=moving&key_by_type=true

def activity_streams(id):
    a_dict = {}
    a_df = pd.DataFrame()
    a_url = "https://www.strava.com/api/v3/activities/"

    streams_list = ['time','distance','latlng','altitude','velocity_smooth','heartrate','cadence','watts','temp',
                    'moving','grade_smooth']
    streams_text = 'time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth'

    a_json = pd.json_normalize(requests.get(a_url + str(id) + '/streams?access_token=' + access_token + 
                                             '&keys=time,distance,latlng,altitude,velocity_smooth,heartrate,cadence,watts,temp,moving,grade_smooth' + 
                                             '&key_by_type=true').json())

    for a in range(0,len(streams_list)):
        try:
            a_df[streams_list[a]] = a_json[str(streams_list[a]) +'.data'][0]
        except:
            a_df[streams_list[a]] = np.nan

    a_df['id'] = id
    idx = activities_overview.index[activities_overview['id'] == id].tolist()[0]

    a_df['date'] = activities_overview['start_date_local'][idx]
    a_df['name'] = activities_overview['name'][idx]
    a_df['type'] = activities_overview['type'][idx]

    return a_df


# ### Load Already Downloaded Activity Details if Present
try:
    activities_details = pd.read_pickle('activities_details.pkl')
except:
    activities_details = pd.DataFrame()

# activities_details.info()
# activities_details.tail()


# ### Download only Details for New Activities
# (https://thispointer.com/pandas-check-if-a-value-exists-in-a-dataframe-using-in-not-in-operator-isin/)

a_details_to_import = []
try:
    a_already_downloaded = activities_details['id'].unique()
except:
    a_already_downloaded = []

for a in activities_overview['id']:
    # faster searching in only one column
    try:
        if a in a_already_downloaded:
            pass
        else:
            a_details_to_import.append(a)

    # if empty dataframe searching in 'id' column will fail
    except:
        if a in activities_details.values:
            pass
        else:
            a_details_to_import.append(a)

print("Number of Activities to Import:  " + str(len(a_details_to_import)))

# Activities that have no details will always show up because they will never have any details added
# a_details_to_import

a_range_l = 0
a_range_h = 89
a_number = len(a_details_to_import)

while a_range_l < a_number:
    if a_range_l > 0:
        print('Waiting...')
        # wait a little over 16m40s to be safe (100 requests per 15min limit)
        time.sleep(1000)

    print('Downloading activities ' + str(a_range_l) + ' to ' + str(a_range_h) +' ...')

    for a in a_details_to_import[a_range_l:a_range_h]:
        print('Downloading activity ', a)
        a_df_curr = activity_streams(a)
        activities_details = activities_details.append(a_df_curr, ignore_index=True) 

    # 90 rather than 100 to be safe
    a_range_l = a_range_l + 90
    a_range_h = a_range_h + 90

print('Done getting details for all new activities.\n')

# print(activities_details.head(2))
# print(activities_details.tail(2))

print("Number of Rows for all Activities Found: ", activities_details.shape)
print("Sum of Moving Time:   ", activities_overview['moving_time'].sum())
print("Sum of Elapsed Time:  ", activities_overview['elapsed_time'].sum())

activities_details.to_pickle('activities_details.pkl')

activities_details.to_csv('activities_details.csv', header=True)

print("\nDETAILED CSV and PKL FILES UPDATED")
print("")
print("EXITING SAROS FIT")