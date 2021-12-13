# strava-app
Authenticate with Strava API and download activities overview and detailed streams for each activity.

---

## For Detailed Step-by-Step Guide for Setting up in AWS:

[Read SarosFit_Strava-App.pdf](SarosFit_Strava-App.pdf)

[Watch YouTube Video](https://www.youtube.com/watch?v=hJLA_NPalJw)

---

## Download Activity Summary and Details from Strava

Strava provides basic information on how to get access to the API at https://developers.strava.com/docs/getting-started/.  
The information from the Strava API page combined with 
https://towardsdatascience.com/using-the-strava-api-and-pandas-to-explore-your-activity-data-d94901d9bfde and other websites 
allowed me to write the code necessary to connect to Strava.

With some additional research I was able to download all my activities and their summary data.  Though, in all my online 
searching I could not find any good examples of how to download all the detailed activity streams associated with each 
Strava activity.  The code to download activity details was mostly written from scratch.

**The value of this notebook is:**
    - example of code to authenticate and connect to the Strava API (follow Strava instructions to create an app)
    - download all activities and their associated summaries to a dataframe
    - download all 11 detailed activity streams for each activity to a dataframe
    - single notebook that authenticates to Strava, downloads activity summaries and downloads activity details

**Additional useful features:**
    - controls the number of requests so they don't exceed Strava's default limits (100 requests/15 min)
    - stores all download activity details in pkl and csv format
    - loads previously downloaded activity details and then only downloads details for new activities

**NEXT STEPS:**
   - Create a separate notebook that loads the pkl file with activity details
       - run basic analysis and create visualizations on the activity details
       - run machine learning models on the activity details to find patterns in heartrate and wattage numbers
---

**Written by:  Sheraz Choudhary**

**Date:        November 2021**

---
