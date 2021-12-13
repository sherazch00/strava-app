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

# AWS Secret Keeper Function
def get_secret(secret_name, region_name = "us-east-1"):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])

    return secret


# ## Connect to Strava -- Get Current Access Token
# (https://towardsdatascience.com/how-i-manage-credentials-in-python-using-aws-secrets-manager-1bd1bf5da598)
client_id = get_secret("<arn for client id>")
client_secret = get_secret("<arn for client secret>")
refresh_token = get_secret("<arn for refresh token>")

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

print("Number of Strava Activities Found: ", activities_overview.shape)
print("")

activities_overview.to_csv('activities_overview.csv', header=True)
print("OVERVIEW CSV FILE UPDATED\n")

print("EXITING SAROS FIT\n")