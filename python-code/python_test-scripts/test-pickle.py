#!/usr/bin/env python
# coding: utf-8

# import libraries
import numpy as np
import pandas as pd

import os
import sys
import subprocess
import pathlib
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import codecs
from codecs import open
from datetime import date
import time

import boto3
import base64
from botocore.exceptions import ClientError

cli = boto3.client('s3')


# ### Load Already Downloaded Activity Details if Present
try:
    # Check to see if there is a local file
    activities_details = pd.read_pickle('activities_details.pkl')
except:
    try:
        # Check the s3 bucket to see if there is a file
        cli.download_file(
            Bucket='sarosfit',
            Key='data/activities_details.pkl',
            Filename='activities_details.pkl')

        activities_details = pd.read_pickle('activities_details.pkl')
    except:
        # Create a new empty dataframe (usually because first run)
        activities_details = pd.DataFrame()

# resolve Error: _pickle.PicklingError: Can't pickle <NA>: it's not the same object as pandas._libs.missing.NA
activities_details['latlng'] = activities_details['latlng'].astype("string")
activities_details = activities_details.replace('<NA>', '')

print(activities_details.iloc[970253])

activities_details.to_pickle('activities_details_test.pkl')

print("EXITING SAROS FIT\n")