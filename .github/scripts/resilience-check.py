import boto3
import os
import time
import sys

AppARN = os.environ['AppARN']
StackARN = os.environ['StackARN']

arh = boto3.client('resiliencehub', region_name='us-east-1')

import_resources = arh.import_resources_to_draft_app_version(
    appArn=AppARN,
    sourceArns=[
        StackARN,
    ]
)

import_status = arh.describe_draft_app_version_resources_import_status(
    appArn=AppARN
)

print(import_status['status'])

while (import_status['status'] == 'Pending' or import_status['status'] == 'InProgress'):
    time.sleep(5)
    import_status = arh.describe_draft_app_version_resources_import_status(
        appArn=AppARN
    )
    print(import_status['status'])
    
if import_status['status'] == 'Failed':
    raise Exception('Resource import failed - ' + str(import_status))
    
publish_app = arh.publish_app_version(
    appArn=AppARN
)

start_assessment = arh.start_app_assessment(
        appArn=AppARN,
        appVersion='release',
        assessmentName='GitHub-actions-assessment'
    )

assessmentARN = start_assessment['assessment']['assessmentArn']

assessment_status = arh.describe_app_assessment(
    assessmentArn=assessmentARN
)

print(assessment_status['assessment']['assessmentStatus'])

while (assessment_status['assessment']['assessmentStatus'] == 'Pending' or assessment_status['assessment']['assessmentStatus'] == 'InProgress'):
    time.sleep(5)
    assessment_status = arh.describe_app_assessment(
        assessmentArn=assessmentARN
    )
    print(assessment_status['assessment']['assessmentStatus'])
    
if assessment_status['assessment']['assessmentStatus'] == 'Failed':
    raise Exception('Assessment failed - ' + str(assessment_status))
    
if assessment_status['assessment']['complianceStatus'] == 'PolicyBreached':
    raise Exception('Policy breached')
else:
    print('Policy met')