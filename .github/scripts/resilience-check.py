import boto3
import os
import time

def resilience_check():
    app_arn = os.environ['AppARN']
    StackARN = os.environ['StackARN']

    arh = boto3.client('resiliencehub', region_name='us-east-1')

    import_resources = arh.import_resources_to_draft_app_version(
        appArn=app_arn,
        sourceArns=[
            StackARN,
        ]
    )

    import_status = arh.describe_draft_app_version_resources_import_status(
        appArn=app_arn
    )

    print('Waiting for import to complete, current status = ' + import_status['status'])

    while (import_status['status'] in ['Pending' or 'InProgress']):
        time.sleep(5)
        import_status = arh.describe_draft_app_version_resources_import_status(
            appArn=app_arn
        )
        print(import_status['status'])
        
    if import_status['status'] == 'Failed':
        raise Exception('Resource import failed - ' + str(import_status))
        
    publish_app = arh.publish_app_version(
        appArn=app_arn
    )

    start_assessment = arh.start_app_assessment(
            appArn=app_arn,
            appVersion='release',
            assessmentName='GitHub-actions-assessment'
        )

    assessmentARN = start_assessment['assessment']['assessmentArn']

    assessment_status = arh.describe_app_assessment(
        assessmentArn=assessmentARN
    )['assessment']['assessmentStatus']

    print(assessment_status)

    while (assessment_status in ['Pending' or 'InProgress']):
        time.sleep(5)
        assessment_status = arh.describe_app_assessment(
            assessmentArn=assessmentARN
        )
        print(assessment_status)
        
    if assessment_status == 'Failed':
        raise Exception('Assessment failed - review the assessment on Resilience Hub for details.')
        
    if assessment_status == 'PolicyBreached':
        raise Exception('Policy breached')
    else:
        print('Policy met')

if __name__ == "__main__":
    resilience_check()
