#!/usr/bin/env python
# coding: utf-8

# https://faun.pub/write-files-from-ec2-to-s3-in-aws-programmatically-716d1a4ef639

# import libraries
import boto3
from datetime import datetime

cli = boto3.client('s3')


cli.put_object(
 Bucket='sarosfit',
 Body='activities_overview.csv',  # local directory file to upload
 Key='data/activities_overview_test.csv')  # folder and name to give file in bucket

print("TEST OVERVIEW FILE UPDATED IN S3 BUCKET\n")

cli.download_file(
  Bucket='sarosfit',
  Key='data/activities_overview_test.csv',  # path and file name to file in bucket
  Filename='activities_overview_test.csv')  # copy with this name in local directory 

print("TEST OVERVIEW FILE DOWNLOADED FROM S3 BUCKET\n")

print("EXITING SAROS FIT\n")