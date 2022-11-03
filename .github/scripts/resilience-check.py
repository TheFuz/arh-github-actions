import boto3
import os

AppARN = os.environ['AppARN']
StackARN = os.environ['StackARN']

arh = boto3.client('resiliencehub', region_name='us-west-2')

print(StackARN)

response = arh.import_resources_to_draft_app_version(
    appArn=AppARN,
    sourceArns=[
        StackARN,
    ]
)

print(response)